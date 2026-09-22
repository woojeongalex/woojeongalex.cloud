"""가사 줄 타이밍 자동 맞춤 — 보컬 스템 음성 인식 + 정답 가사와 단어 정렬.

사용: python align_lyrics.py <보컬 wav> <가사 json(lines)> <출력 json> [모델] [novad|vad] [en|ko]

한국어는 음절 단위로 맞춘다. 인식 결과와 가사의 띄어쓰기·조사가 자주 달라서
("그림자가" / "그림자 가") 어절 단위로는 대부분의 줄을 놓친다.
"""
import difflib, json, re, sys, time
from faster_whisper import WhisperModel

vocals, lyrics_path, out_path = sys.argv[1:4]
model_name = sys.argv[4] if len(sys.argv) > 4 else "small.en"
# 무음 필터는 작게 부른 구간까지 잘라 인식이 빠질 수 있다. "novad" 로 끈다.
use_vad = not (len(sys.argv) > 5 and sys.argv[5] == "novad")
language = sys.argv[6] if len(sys.argv) > 6 else "en"
by_syllable = language == "ko"
lines = [l["text"] for l in json.load(open(lyrics_path, encoding="utf-8"))["lines"]]


def norm(w: str) -> str:
    # \w 는 유니코드 글자라 한글도 남는다. 문장부호만 지운다.
    w = w.lower().replace("’", "'").replace("‘", "'")
    return re.sub(r"[^\w']", "", w)


def units(text: str) -> list[str]:
    """맞춤 단위 — 영어는 단어, 한국어는 글자(음절)."""
    if by_syllable:
        return [c for c in norm(text.replace(" ", "")) if c != "'"]
    return [w for w in (norm(x) for x in text.split()) if w]


# 정답 가사 단위 — (단위, 줄 번호, 줄 안 위치)
lyric_words = []
for li, line in enumerate(lines):
    for k, w in enumerate(units(line)):
        lyric_words.append((w, li, k))

t0 = time.time()
model = WhisperModel(model_name, device="cpu", compute_type="int8")
# 노래는 같은 구절이 반복돼서 이전 문장을 조건으로 주면 같은 줄을 계속 되풀이하는
# 환각이 잦다. 끄고, 가사 첫 부분을 힌트로 준다.
segments, _ = model.transcribe(
    vocals,
    language=language,
    word_timestamps=True,
    vad_filter=use_vad,
    condition_on_previous_text=False,
    initial_prompt=" ".join(lines[:12]),
)
rec = []
for seg in segments:
    for w in seg.words or []:
        parts = units(w.word)
        # 한 어절 안의 음절에는 어절 길이를 음절 수로 나눠 시각을 준다.
        for k, p in enumerate(parts):
            t = w.start + (w.end - w.start) * k / max(1, len(parts))
            rec.append((p, t, w.end))
print(f"인식 단어 {len(rec)}개 / 가사 단어 {len(lyric_words)}개 ({time.time()-t0:.0f}s, {model_name}, vad={use_vad})")

# 인식 결과와 정답 가사를 순서대로 맞춘다 — 반복되는 후렴도 순서대로 짝지어진다.
sm = difflib.SequenceMatcher(a=[w for w, _, _ in lyric_words], b=[w for w, _, _ in rec], autojunk=False)
word_time: dict[int, float] = {}
for block in sm.get_matching_blocks():
    for k in range(block.size):
        word_time[block.a + k] = rec[block.b + k][1]
print(f"맞춘 단어 {len(word_time)}/{len(lyric_words)} ({100*len(word_time)/len(lyric_words):.0f}%)")

# 줄 시작 = 그 줄에서 처음 맞은 단위 시각 − (그 앞의 단위 수 × 평균 길이)
# 영어 단어는 0.3초, 한국어 음절은 0.2초 정도로 부른다.
AVG_WORD = 0.2 if by_syllable else 0.3
starts: list[float | None] = [None] * len(lines)
sources: list[str] = ["보간"] * len(lines)
for idx, (w, li, k) in enumerate(lyric_words):
    if starts[li] is None and idx in word_time:
        starts[li] = max(0.0, word_time[idx] - k * AVG_WORD)
        sources[li] = "인식" if k == 0 else f"인식(+{k}{'음절' if by_syllable else '단어'})"

# 시간이 거꾸로 가는 줄은 잘못 맞은 것으로 보고 비운다.
last = -1.0
for i, s in enumerate(starts):
    if s is None:
        continue
    if s < last:
        starts[i] = None
        sources[i] = "보간"
    else:
        last = s

# 비어 있는 줄은 앞뒤로 맞은 줄 사이를 단어 수 비율로 채운다.
wc = [max(1, len(l.split())) for l in lines]
i = 0
while i < len(lines):
    if starts[i] is not None:
        i += 1
        continue
    j = i
    while j < len(lines) and starts[j] is None:
        j += 1
    prev_i = i - 1
    a = starts[prev_i] if prev_i >= 0 else 0.0
    b = starts[j] if j < len(lines) else None
    if b is None:  # 끝부분 — 줄당 단어 수 × 0.4초로 이어 붙인다
        t = a + (wc[prev_i] * 0.4 if prev_i >= 0 else 0)
        for k in range(i, j):
            starts[k] = round(t, 2); t += wc[k] * 0.4
    else:
        span = [wc[prev_i]] if prev_i >= 0 else []
        total = sum(wc[prev_i:j]) if prev_i >= 0 else sum(wc[i:j]) + 1
        acc = wc[prev_i] if prev_i >= 0 else 0
        for k in range(i, j):
            starts[k] = round(a + (b - a) * acc / total, 2); acc += wc[k]
    i = j

matched = sum(1 for s in sources if s != "보간")
print(f"인식으로 맞춘 줄 {matched}/{len(lines)}, 보간 {len(lines)-matched}")
json.dump({"lines": [{"text": l, "start": round(s, 2)} for l, s in zip(lines, starts)]},
          open(out_path, "w", encoding="utf-8"), ensure_ascii=False)
json.dump(sources, open(out_path.replace(".json", "_sources.json"), "w", encoding="utf-8"), ensure_ascii=False)

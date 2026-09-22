# song-prep-pipeline.md — Suno 곡을 노래방 챌린지로 준비하기

> 적용 범위: `woojeongai/tools/song_prep/` · 챌린지 악보(`challenge_charts`)를 만드는 관리자 작업 전체

---

## 0. 한 줄 요약

```bash
cd woojeongai/tools/song_prep
export SONG_PREP_PASSWORD=...          # 관리자 비밀번호. 코드·커밋·로그에 남기지 않는다
python3 prepare_song.py 완성곡.wav 가사.txt --title "곡 제목" [--language ko]
```

완성곡 + 가사 텍스트만 있으면 된다. 끝나면 "확인 권장" 가사 줄 목록이 나오고, 그 줄만 스튜디오(`/music-challenge/<id>/studio`)에서 들어 보고 고친다.

**실행 위치**: WSL/리눅스 + Docker. EC2(메모리 1GB)에서는 돌리지 않는다.

---

## 1. 단계와 판단 근거

| 단계 | 도구 | 근거 |
|---|---|---|
| 보컬/반주 분리 | Demucs `htdemucs --two-stems vocals` (CPU) | 완성곡을 그대로 넣으면 반주 음까지 정답 음표로 잡힌다 |
| 챌린지 등록·가사 저장 | 백엔드 API | 한글은 UTF-8 multipart 로 직접 만든다 — curl 인자로 보내면 CP949 로 깨졌다 |
| 정답 멜로디 | 백엔드(스템 업로드 시 자동) | `librosa_melody_extractor_adapter.py` — pyin 16kHz·20ms, 보컬 후처리 |
| 가사 타이밍 인식 ×2 | faster-whisper medium + small, VAD 끔 | 한 번의 인식은 맞았는지 검증할 수 없다. 서로 독립인 두 결과의 일치로 검증한다 |
| 두 결과 합치기 | `combine_alignments.py` — 곡 전체 경로 선택(동적 계획법) | 후렴이 반복되면 두 모델이 서로 다른 곳에서 다른 회차에 붙인다. 줄 하나씩 판정하면 뒤따르는 줄이 몰린다 |
| 점검 보고 | `prepare_song.py` | 주 음역 · 짧은 조각 비율 · 옥타브 튐 · 끝부분 무음 · 확인 권장 줄 |

한국어는 `--language ko` — 다국어 모델을 쓰고 **음절 단위**로 맞춘다(인식 결과와 가사의 띄어쓰기·조사가 달라 어절 단위로는 대부분 놓친다).

---

## 2. 자원 한도 (반드시 유지)

| 컨테이너 | 메모리 | CPU |
|---|---|---|
| Demucs | 5GB | 6 |
| Whisper medium | 4GB | 6 |
| Whisper small | 3GB | 6 |

WSL 기본 메모리는 PC 램의 절반이고 백엔드·DB 도 같은 가상머신에서 돈다. **한도 없이 Whisper medium 을 돌렸다가 WSL 전체가 멈춰** 백엔드·프론트가 동시에 죽었다(2026-09-22). 한도에 걸려 종료(exit 137)되면 도구는 남은 결과로 계속한다 — 다국어 medium 은 4GB 에서 종료되는 경우가 있다.

모델 캐시(약 4GB)는 `~/.cache/song_prep/.cache` 한곳에 둔다. 곡마다 두면 매번 다시 받는다.

---

## 3. 옵션

| 옵션 | 용도 |
|---|---|
| `--challenge-id N` | 이미 등록한 챌린지에 붙인다(가사·스템·타이밍을 다시 만든다) |
| `--vocals v.wav --backing b.wav` | Suno Get Stems 로 받은 스템이 있으면 분리를 건너뛴다 — 분리보다 품질이 좋다 |
| `--language ko` | 한국어 곡 |
| `--api URL` / `SONG_PREP_API` | 기본 `http://localhost:8000` |
| `--username` / `SONG_PREP_USERNAME` | 관리자 계정 |

---

## 4. 결과 확인 기준

- **주 음역(5~95%)** 이 부르는 사람 음역과 맞는지
- **0.15초 미만 조각** 15% 이하 (실측: 3곡 3~12%)
- **옥타브 튐** 이 곡 구조를 따라 규칙적으로 반복되면 실제 멜로디 도약이다(오류 아님)
- **끝부분 무음 경고** 가 나오면 연주로 끝나는 곡인지 들어 본다
- **확인 권장 줄**(`골라냄`·`추정`) 만 스튜디오에서 클릭해 들어 본다 — 그 줄 2초 앞부터 재생된다

## 5. 한계

- 멜로디 악기 연주곡은 이 도구로 만들지 않는다. Demucs 는 보컬/반주만 나누므로 멜로디 악기 하나를 떼어 내지 못한다 — Suno 의 악기별 스템을 스튜디오에서 올린다.
- 가사 타이밍은 줄 시작만 맞춘다. 단어별 채움은 줄 안에서 균등하게 채워진다.

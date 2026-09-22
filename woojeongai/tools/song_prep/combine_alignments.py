"""두 번의 독립 인식(small / medium) 결과를 합친다 — 곡 전체에서 가장 그럴듯한 경로를 고른다.

줄마다 후보는 두 개(small 값, medium 값)다. 줄 사이 간격이 그 줄의 단어 수로 예상한
길이와 얼마나 맞는지를 비용으로 삼아, 전체 비용이 가장 작은 조합을 동적 계획법으로 찾는다.
간격이 0 이하(시간 역전)면 불가능한 경로로 친다. 인식이 아니라 보간으로 채운 후보는
조금 불리하게 둔다.

줄 하나씩 따로 판정하면 안 된다. 후렴이 글자 그대로 세 번 나오는 곡(Close Enough To
Touch)에서 medium 이 첫 후렴을 두 번째 회차에 붙였고, "엇갈리면 큰 모델"로 고르자
뒤따르는 15줄이 4초 안에 몰렸다. 앞뒤 흐름과 함께 봐야 가려진다.
"""
import json, math, sys

song = sys.argv[1] if len(sys.argv) > 1 else "still"
load = lambda p: json.load(open(f"/data/{song}_{p}.json", encoding="utf-8"))
a, b = load("timed")["lines"], load("timed_medium")["lines"]
sa, sb = load("timed_sources"), load("timed_medium_sources")
n = len(a)
AGREE = 0.3
SEC_PER_WORD = 0.45  # 이 곡들에서 한 줄을 부르는 데 드는 시간 / 단어 수의 대략값
INTERP_PENALTY = 0.6
wc = [max(1, len(l["text"].split())) for l in a]

# 후보: (시각, 출처, 인식 여부)
cands = [[(a[i]["start"], "small", sa[i] != "보간"), (b[i]["start"], "medium", sb[i] != "보간")] for i in range(n)]


def gap_cost(i: int, t_prev: float, t_cur: float) -> float:
    gap = t_cur - t_prev
    if gap <= 0.05:
        return math.inf
    return math.log(gap / (wc[i - 1] * SEC_PER_WORD)) ** 2


def node_cost(c) -> float:
    return 0.0 if c[2] else INTERP_PENALTY


cost = [[node_cost(c) for c in cands[0]]]
back: list[list[int]] = [[-1, -1]]
for i in range(1, n):
    row, brow = [], []
    for c in cands[i]:
        best, arg = math.inf, 0
        for j, p in enumerate(cands[i - 1]):
            v = cost[i - 1][j] + gap_cost(i, p[0], c[0])
            if v < best:
                best, arg = v, j
        row.append(best + node_cost(c))
        brow.append(arg)
    cost.append(row)
    back.append(brow)

k = min(range(2), key=lambda j: cost[-1][j])
if math.isinf(cost[-1][k]):
    sys.exit("가능한 경로가 없습니다 — 두 결과 모두 시간 순서가 깨져 있습니다.")
pick = [0] * n
for i in range(n - 1, -1, -1):
    pick[i] = k
    k = back[i][k]

final, status = [], []
for i in range(n):
    t, src, recog = cands[i][pick[i]]
    agree = sa[i] != "보간" and sb[i] != "보간" and abs(a[i]["start"] - b[i]["start"]) <= AGREE
    if agree:
        t = (a[i]["start"] + b[i]["start"]) / 2
        status.append("확정")
    elif not recog:
        status.append("추정")
    elif (sa[i] != "보간") and (sb[i] != "보간"):
        status.append(f"골라냄({src})")
    else:
        status.append("한쪽")
    final.append(t)

counts: dict[str, int] = {}
for s in status:
    key = "골라냄" if s.startswith("골라냄") else s
    counts[key] = counts.get(key, 0) + 1
print("줄 상태:", counts, f"| small 쓴 줄 {sum(1 for p in pick if p == 0)}, medium {sum(1 for p in pick if p == 1)}")
print("확인 권장 (골라냄·추정):")
for i in range(n):
    if status[i].startswith("골라냄") or status[i] == "추정":
        print(f"  {i+1:2d}번 {final[i]:6.2f}s  [{status[i]}]  small {a[i]['start']:.2f} / medium {b[i]['start']:.2f}  {a[i]['text']}")
json.dump({"lines": [{"text": l["text"], "start": round(t, 2)} for l, t in zip(a, final)]},
          open(f"/data/{song}_timed_final.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(status, open(f"/data/{song}_timed_final_status.json", "w", encoding="utf-8"), ensure_ascii=False)

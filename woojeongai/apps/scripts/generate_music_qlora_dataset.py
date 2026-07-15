"""음악 추천 QLoRA 학습용 합성 데이터셋 생성: python3 generate_music_qlora_dataset.py

ship의 EXAONE-3.5-7.8B(채팅 모드)를 "교사" 모델로 써서, 상황/기분 기반 곡
추천 대화 예시를 다양한 카테고리별로 생성하고 JSONL로 저장한다.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

OUTPUT_PATH = (
    Path(__file__).resolve().parent / "qlora_data" / "music_mood_recommendations.jsonl"
)
EXAMPLES_PER_CATEGORY = 5

CATEGORIES = [
    "우울하거나 힘들 때 위로가 되는 노래",
    "신나는 파티나 모임에 어울리는 노래",
    "잔잔하게 휴식할 때 듣는 노래",
    "공부나 작업에 집중할 때 듣는 노래",
    "운동할 때 듣는 노래",
    "드라이브할 때 듣는 노래",
    "비 오는 날 듣기 좋은 노래",
    "이별 후에 듣는 노래",
    "설레는 감정이나 썸 탈 때 듣는 노래",
    "잠이 안 오는 새벽에 듣는 노래",
    "상쾌한 아침에 듣는 노래",
    "카페에서 듣기 좋은 노래",
    "여행 갈 때 듣는 노래",
    "옛 추억이 그리울 때 듣는 노래",
]

SYSTEM_PROMPT = (
    "너는 사용자의 상황이나 기분에 맞춰 노래를 추천해주는 다정한 음악 큐레이터야. "
    "실제 존재하는 곡(제목+가수)을 자연스럽게 언급하면서, 왜 그 곡이 이 상황에 어울리는지 "
    "짧고 따뜻한 말투로 설명해. 곡은 매번 다르게, 특정 가수나 곡에 치우치지 않도록 다양하게 추천해."
)


def generate_batch(category: str) -> list[dict[str, str]]:
    import requests

    base_url = os.getenv("LOCAL_LLM_BASE_URL", "").rstrip("/")
    model = os.getenv("LOCAL_LLM_MODEL") or "EXAONE-3.5-7.8B-Instruct-AWQ"
    prompt = (
        f'"{category}" 상황을 가정한 사용자 질문과, 그에 대한 추천 답변 쌍을 '
        f"{EXAMPLES_PER_CATEGORY}개 만들어줘. 질문은 매번 표현을 다르게 하고, "
        "답변마다 다른 곡을 추천해. 아래 JSON 배열 형식으로만 답해, 다른 설명은 붙이지 마:\n"
        '[{"question": "...", "answer": "..."}, ...]'
    )
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1200,
        },
        timeout=120,
    )
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"].strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        print(f"  경고: JSON 배열을 못 찾음, 건너뜀 ({category})")
        return []
    try:
        pairs = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        print(f"  경고: JSON 파싱 실패, 건너뜀 ({category})")
        return []
    return [p for p in pairs if p.get("question") and p.get("answer")]


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    all_examples: list[dict] = []

    for category in CATEGORIES:
        print(f"생성 중: {category}")
        pairs = generate_batch(category)
        print(f"  -> {len(pairs)}개 생성됨")
        for pair in pairs:
            all_examples.append(
                {
                    "messages": [
                        {"role": "user", "content": pair["question"]},
                        {"role": "assistant", "content": pair["answer"]},
                    ]
                }
            )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"\n총 {len(all_examples)}개 예시 저장됨: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

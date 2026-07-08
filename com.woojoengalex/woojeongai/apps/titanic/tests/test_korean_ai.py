import pytest
import ollama
from kiwipiepy import Kiwi

kiwi = Kiwi()


def run_korean_ai(user_text: str) -> str:
    kiwi.global_config.space_tolerance = 2
    cleaned_text = user_text

    tokens = kiwi.tokenize(cleaned_text)
    nouns = [t.form for t in tokens if t.tag.startswith('NN')]
    print(f"\n추출된 핵심 명사: {nouns}")

    response = ollama.chat(
        model='anpigon/eeve-korean-10.8b:latest',
        messages=[{'role': 'user', 'content': cleaned_text}]
    )
    return response['message']['content']


@pytest.mark.ollama
def test_ollama_kiwi():
    question = "자연어처리는 넘흐 재밌어요. 올라마와 키위 라이브러리의 장점을 짧게 요약해줘."
    answer = run_korean_ai(question)
    print(f"\n[AI 답변]\n{answer}")
    assert isinstance(answer, str) and len(answer) > 0


if __name__ == "__main__":
    question = "타이타닉의 생존자는 몇 명이야?."
    answer = run_korean_ai(question)
    print(f"\n[AI 답변]\n{answer}")

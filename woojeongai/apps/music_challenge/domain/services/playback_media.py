"""재생용 사본의 자리를 정하는 규칙.

분석에는 원본 무압축 WAV 가 필요하지만 재생에는 너무 크다(4분에 40MB 남짓).
원본은 그대로 두고 같은 자리에 MP3 를 하나 더 둔다 — 약 8배 작다.

키를 DB 에 따로 저장하지 않고 이 규칙으로 찾는다. 그래서 마이그레이션이 필요 없고,
아직 변환하지 않은 곡은 원본으로 재생된다.

만드는 쪽(업로드)과 찾는 쪽(재생 URL)이 같은 규칙을 써야 하므로 여기 한 곳에 둔다.
"""


def playback_key_for(key: str) -> str | None:
    """재생용 사본을 둘 키. wav 가 아니면 만들 것이 없다(이미 압축된 것이다)."""
    root, dot, ext = key.rpartition(".")
    return f"{root}.mp3" if dot and ext.lower() == "wav" else None

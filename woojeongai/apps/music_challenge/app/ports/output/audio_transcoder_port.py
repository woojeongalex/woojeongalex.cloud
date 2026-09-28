from abc import ABC, abstractmethod


class AudioTranscoderPort(ABC):
    @abstractmethod
    async def to_mp3(self, data: bytes) -> bytes | None:
        """재생용 MP3 로 줄인다. 실패하면 None.

        분석에는 원본 무압축 WAV 가 필요하지만 재생에는 너무 크다(4분에 40MB 남짓).
        원본은 그대로 두고 재생용 사본만 따로 만든다 — 약 8배 작아진다.

        변환에 실패해도 곡 등록 자체는 살아야 하므로 예외 대신 None 을 준다.
        재생은 MP3 가 없으면 원본으로 돌아간다.
        """
        ...

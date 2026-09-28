from abc import ABC, abstractmethod


class MediaStoragePort(ABC):
    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str) -> str: ...

    @abstractmethod
    async def presigned_url(self, key: str) -> str: ...

    @abstractmethod
    async def playback_url(self, key: str) -> str:
        """브라우저에 들려줄 URL.

        분석에는 원본 무압축 WAV 가 필요하지만 재생에는 너무 크다. 4분짜리 곡이
        40MB 가 넘어 LTE 에서 곡이 시작되기까지 십몇 초가 걸렸다. 그래서 같은 자리에
        MP3 를 하나 더 두고, 재생은 그쪽을 준다(약 8배 작다).

        MP3 가 없으면 원본 키로 돌아간다 — 아직 변환하지 않은 곡도 재생은 된다.
        """
        ...

    @abstractmethod
    async def download(self, key: str) -> bytes: ...

from abc import ABC, abstractmethod


class MediaStoragePort(ABC):
    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str) -> str: ...

    @abstractmethod
    async def presigned_url(self, key: str) -> str: ...

    @abstractmethod
    async def download(self, key: str) -> bytes: ...

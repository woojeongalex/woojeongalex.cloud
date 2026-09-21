from abc import ABC, abstractmethod

from music_challenge.app.dtos.chart_dto import (
    ChartResult,
    UploadStemsCommand,
    UploadStemsResult,
)
from music_challenge.domain.value_objects.chart_vo import LyricLine


class GetChartUseCase(ABC):
    @abstractmethod
    async def get(self, challenge_id: int) -> ChartResult: ...


class UploadStemsUseCase(ABC):
    @abstractmethod
    async def upload(self, command: UploadStemsCommand) -> UploadStemsResult:
        """스템을 저장하고 상태를 processing 으로 둔다. 추출은 BuildChart 가 한다."""


class BuildChartUseCase(ABC):
    @abstractmethod
    async def build(
        self, challenge_id: int, vocal_key: str, vocal_bytes: bytes
    ) -> None:
        """정답 멜로디를 추출해 저장한다. 요청 밖(백그라운드)에서 실행된다.

        vocal_key 는 이 추출이 어느 업로드의 것인지 가리킨다. 처리 중에 새 스템이
        올라왔다면 결과를 버려서, 늦게 끝난 옛 작업이 새 결과를 덮지 못하게 한다.
        """


class UpdateLyricsUseCase(ABC):
    @abstractmethod
    async def update(
        self, challenge_id: int, lines: list[LyricLine]
    ) -> ChartResult: ...

from abc import ABC, abstractmethod

from music_challenge.app.dtos.rhythm_dto import (
    RhythmChartResult,
    RhythmPlayResult,
    RhythmRankingEntry,
    RhythmSheetResult,
    RhythmSongItem,
    RhythmStanding,
    SubmitRhythmPlayCommand,
)
from music_challenge.domain.value_objects.rhythm_vo import RhythmDifficulty


class GetRhythmChartUseCase(ABC):
    @abstractmethod
    async def get(self, challenge_id: int) -> RhythmChartResult:
        """채보 목록(노트 없이 키·난이도·레벨)과 생성 상태."""

    @abstractmethod
    async def get_sheet(
        self, challenge_id: int, keys: int, difficulty: RhythmDifficulty
    ) -> RhythmSheetResult: ...


class RequestRhythmBuildUseCase(ABC):
    @abstractmethod
    async def request(self, challenge_id: int) -> tuple[RhythmChartResult, str, str]:
        """상태를 processing 으로 두고 (결과, job_id, 원곡 S3 키)를 돌려준다.

        실제 분석은 BuildRhythmChart 가 요청 밖(백그라운드)에서 한다.
        """


class BuildRhythmChartUseCase(ABC):
    @abstractmethod
    async def build(self, challenge_id: int, job_id: str, source_key: str) -> None:
        """원곡을 받아 분석하고 채보 6개를 저장한다. 그 사이 새 요청이 있었으면 버린다."""


class SubmitRhythmPlayUseCase(ABC):
    @abstractmethod
    async def submit(self, command: SubmitRhythmPlayCommand) -> RhythmPlayResult: ...


class GetRhythmRankingUseCase(ABC):
    @abstractmethod
    async def get(
        self,
        challenge_id: int,
        keys: int,
        difficulty: RhythmDifficulty,
        limit: int,
        username: str | None,
    ) -> tuple[list[RhythmRankingEntry], RhythmStanding | None]: ...


class ListRhythmSongsUseCase(ABC):
    @abstractmethod
    async def list(self) -> list[RhythmSongItem]:
        """리듬 게임 메뉴의 곡 목록 — 활성 챌린지 중 채보가 준비된 곡만."""

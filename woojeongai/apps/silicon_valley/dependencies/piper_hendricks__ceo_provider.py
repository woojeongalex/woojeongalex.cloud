from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.adapter.outbound.repositories.piper_hendricks__ceo_repository import (
    HendricksCeoRepository,
)
from silicon_valley.adapter.outbound.repositories.song_rag_repository import (
    SongRagRepository,
)
from silicon_valley.app.ports.input.piper_hendricks__ceo_use_case import (
    HendricksCeoUseCase,
)
from silicon_valley.app.ports.output.piper_hendricks__ceo_port import HendricksCeoPort
from silicon_valley.app.ports.output.song_rag_port import SongRagPort
from silicon_valley.app.use_cases.piper_hendricks__ceo_interactor import (
    HendricksCeoInteractor,
)


def get_hendricks_ceo_repository(
    db: AsyncSession = Depends(get_db),
) -> HendricksCeoPort:
    return HendricksCeoRepository(session=db)


def get_song_rag_repository(db: AsyncSession = Depends(get_db)) -> SongRagPort:
    return SongRagRepository(session=db)


def get_hendricks_ceo_use_case(
    repository: HendricksCeoPort = Depends(get_hendricks_ceo_repository),
    song_rag: SongRagPort = Depends(get_song_rag_repository),
) -> HendricksCeoUseCase:
    return HendricksCeoInteractor(repository=repository, song_rag=song_rag)

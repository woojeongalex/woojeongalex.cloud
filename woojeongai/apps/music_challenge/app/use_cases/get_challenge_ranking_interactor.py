from fastapi import HTTPException

from music_challenge.app.dtos.ranking_dto import MyStanding, RankingEntry
from music_challenge.app.ports.input.ranking_use_case import GetChallengeRankingUseCase
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.app.ports.output.ranking_query_port import RankingQueryPort
from music_challenge.app.ports.output.user_lookup_port import UserLookupPort


class GetChallengeRankingInteractor(GetChallengeRankingUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        ranking: RankingQueryPort,
        user_lookup: UserLookupPort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._ranking = ranking
        self._user_lookup = user_lookup

    async def get(
        self, challenge_id: int, limit: int, username: str | None
    ) -> tuple[list[RankingEntry], MyStanding | None]:
        if not await self._challenge_repo.find_by_id(challenge_id):
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")
        entries = await self._ranking.challenge_ranking(challenge_id, limit)
        # 내 순위는 토큰의 username 으로만 찾는다(클라이언트가 user_id 를 지정하지 못한다).
        user_id = (
            await self._user_lookup.find_id_by_username(username) if username else None
        )
        me = await self._ranking.my_standing(challenge_id, user_id) if user_id else None
        return entries, me

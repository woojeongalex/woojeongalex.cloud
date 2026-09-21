from music_challenge.app.dtos.history_dto import SubmissionHistoryItem
from music_challenge.app.ports.input.history_use_case import GetMyHistoryUseCase
from music_challenge.app.ports.output.submission_repository_port import (
    SubmissionRepositoryPort,
)
from music_challenge.app.ports.output.user_lookup_port import UserLookupPort


class GetMyHistoryInteractor(GetMyHistoryUseCase):
    def __init__(
        self,
        submission_repo: SubmissionRepositoryPort,
        user_lookup: UserLookupPort,
    ) -> None:
        self._submission_repo = submission_repo
        self._user_lookup = user_lookup

    async def get(self, username: str, limit: int) -> list[SubmissionHistoryItem]:
        # 토큰의 username 으로만 조회한다. 남의 기록을 볼 수 있으면 안 되므로
        # 클라이언트가 user_id 를 지정할 여지를 두지 않는다.
        user_id = await self._user_lookup.find_id_by_username(username)
        if user_id is None:
            return []
        return await self._submission_repo.find_history_by_user(user_id, limit)

from abc import ABC, abstractmethod


class UserLookupPort(ABC):
    """JWT 의 sub(username)를 users.id 로 바꾸기 위한 포트.

    토큰에는 username 만 들어 있는데 제출물은 users.id 를 FK 로 참조한다.
    클라이언트가 보낸 user_id 를 그대로 믿으면 랭킹을 위조할 수 있으므로,
    서버가 검증된 토큰의 username 으로 직접 조회한다.
    """

    @abstractmethod
    async def find_id_by_username(self, username: str) -> int | None: ...

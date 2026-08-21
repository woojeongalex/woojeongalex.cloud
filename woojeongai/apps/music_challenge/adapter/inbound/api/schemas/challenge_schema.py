from pydantic import BaseModel


class ChallengeResponse(BaseModel):
    id: int
    title: str
    description: str
    music_url: str
    challenge_type: str
    is_active: bool


class ChallengesListResponse(BaseModel):
    items: list[ChallengeResponse]
    total: int

from fastapi import APIRouter

from music_challenge.adapter.inbound.api.v1.challenges_router import challenges_router
from music_challenge.adapter.inbound.api.v1.submissions_router import submissions_router

music_challenge_router = APIRouter(prefix="/music_challenge", tags=["music_challenge"])
music_challenge_router.include_router(challenges_router)
music_challenge_router.include_router(submissions_router)

__all__ = ["music_challenge_router"]

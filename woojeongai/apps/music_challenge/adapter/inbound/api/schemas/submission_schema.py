from pydantic import BaseModel


class EvaluationResponse(BaseModel):
    id: int
    submission_id: int
    score: int
    feedback: str
    next_challenge_id: int | None

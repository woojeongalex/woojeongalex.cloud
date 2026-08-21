from music_challenge.adapter.inbound.api.schemas.submission_schema import EvaluationResponse
from music_challenge.app.dtos.evaluation_dto import EvaluationResult


def evaluation_result_to_response(result: EvaluationResult) -> EvaluationResponse:
    return EvaluationResponse(
        id=result.id,
        submission_id=result.submission_id,
        score=result.score,
        feedback=result.feedback,
        next_challenge_id=result.next_challenge_id,
    )

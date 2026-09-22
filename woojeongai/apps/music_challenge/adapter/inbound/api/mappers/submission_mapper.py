from music_challenge.adapter.inbound.api.schemas.submission_schema import (
    EvaluationResponse,
    KaraokeResultResponse,
    SubmissionHistoryItemResponse,
)
from music_challenge.app.dtos.evaluation_dto import EvaluationResult
from music_challenge.app.dtos.history_dto import SubmissionHistoryItem


def evaluation_result_to_response(result: EvaluationResult) -> EvaluationResponse:
    return EvaluationResponse(
        id=result.id,
        submission_id=result.submission_id,
        score=result.score,
        feedback=result.feedback,
        next_challenge_id=result.next_challenge_id,
        pitch_score=result.pitch_score,
        rhythm_score=result.rhythm_score,
        tempo=result.tempo,
        karaoke=(
            KaraokeResultResponse(
                score=result.karaoke.score,
                pitch_accuracy=result.karaoke.pitch_accuracy,
                timing_accuracy=result.karaoke.timing_accuracy,
                rank=result.karaoke.rank,
                best_score=result.karaoke.best_score,
                is_personal_best=result.karaoke.is_personal_best,
            )
            if result.karaoke
            else None
        ),
    )


def history_item_to_response(
    item: SubmissionHistoryItem,
) -> SubmissionHistoryItemResponse:
    return SubmissionHistoryItemResponse(
        submission_id=item.submission_id,
        challenge_id=item.challenge_id,
        challenge_title=item.challenge_title,
        challenge_type=item.challenge_type,
        media_type=item.media_type,
        created_at=item.created_at,
        score=item.score,
        pitch_score=item.pitch_score,
        rhythm_score=item.rhythm_score,
    )

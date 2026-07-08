"""세션 → 녹음 → 분석 3단 INSERT (보컬·악기·스피치 공통)."""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def save_three_part_bundle(
    db: AsyncSession,
    evaluation: Any,
    recording: Any,
    analysis: Any,
    *,
    recording_fk_attr: str,
    analysis_fk_attr: str,
    log_label: str,
) -> tuple[Any, Any, Any]:
    db.add(evaluation)
    await db.flush()
    eval_id = evaluation.id
    assert eval_id is not None

    setattr(recording, recording_fk_attr, eval_id)
    db.add(recording)
    await db.flush()
    recording_id = recording.id
    assert recording_id is not None

    setattr(analysis, analysis_fk_attr, recording_id)
    db.add(analysis)
    await db.commit()
    await db.refresh(evaluation)
    await db.refresh(recording)
    await db.refresh(analysis)
    logger.info(
        "[MUSIC][%s][repo] eval=%s recording=%s analysis=%s",
        log_label,
        evaluation.id,
        recording.id,
        analysis.id,
    )
    return evaluation, recording, analysis

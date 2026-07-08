from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from music.adapter.outbound.orm.vocal_maestro_analyzer_model import (
    AiVocalAnalysisEntity,
    SingEvaluationEntity,
)
from music.adapter.outbound.orm.speech_oracle_analyst_model import (
    SpeechEvaluationEntity,
    SpeechFeedbackAnalysisEntity,
)
from titanic.adapter.outbound.orm.passenger_orm import PersonOrm

admin_stats_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_stats_router.get("/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    try:
        total_evals = await db.scalar(
            select(func.count()).select_from(SingEvaluationEntity)
        ) or 0

        avg_score_raw = await db.scalar(
            select(func.round(
                func.avg((AiVocalAnalysisEntity.pitch_score + AiVocalAnalysisEntity.rhythm_score) / 2.0),
                1
            )).where(
                AiVocalAnalysisEntity.pitch_score.is_not(None),
                AiVocalAnalysisEntity.rhythm_score.is_not(None),
            )
        )
        avg_score = float(avg_score_raw) if avg_score_raw is not None else 0.0

        passenger_count = await db.scalar(
            select(func.count()).select_from(PersonOrm)
        ) or 0

        return {
            "totalEvals":      total_evals,
            "avgScore":        avg_score,
            "intentLogCount":  0,   # intent_logs 테이블 없음 — 추후 확장 시 여기서 COUNT
            "passengerCount":  passenger_count,
        }
    except Exception:
        return {"totalEvals": 0, "avgScore": 0.0, "intentLogCount": 0, "passengerCount": 0}


@admin_stats_router.get("/service-stats")
async def get_service_stats(db: AsyncSession = Depends(get_db)):
    try:
        total_evals    = await db.scalar(select(func.count()).select_from(SingEvaluationEntity))    or 0
        total_analyses = await db.scalar(select(func.count()).select_from(AiVocalAnalysisEntity))   or 0
        total_speech   = await db.scalar(select(func.count()).select_from(SpeechEvaluationEntity))  or 0
        total_feedback = await db.scalar(select(func.count()).select_from(SpeechFeedbackAnalysisEntity)) or 0

        total_passengers = await db.scalar(select(func.count()).select_from(PersonOrm)) or 0
        survived_count   = await db.scalar(
            select(func.count()).select_from(PersonOrm).where(PersonOrm.survived.is_not(None))
        ) or 0

        vocal_eval_rate     = min(round((total_analyses / total_evals) * 100), 100) if total_evals > 0 else 0
        passenger_data_rate = min(round((survived_count / total_passengers) * 100), 100) if total_passengers > 0 else 0
        speech_eval_rate    = min(round((total_feedback / total_speech) * 100), 100) if total_speech > 0 else 0

        return {
            "vocalEvalRate":     vocal_eval_rate,
            "aiAccuracyRate":    0,   # intent_logs 테이블 없음
            "passengerDataRate": passenger_data_rate,
            "speechEvalRate":    speech_eval_rate,
        }
    except Exception:
        return {"vocalEvalRate": 0, "aiAccuracyRate": 0, "passengerDataRate": 0, "speechEvalRate": 0}


@admin_stats_router.get("/intent-distribution")
async def get_intent_distribution():
    # intent_logs 테이블 없음 — 추후 테이블 생성 시 여기서 GROUP BY intent 집계
    return {"distribution": []}


@admin_stats_router.get("/passengers")
async def get_admin_passengers(db: AsyncSession = Depends(get_db)):
    try:
        total = await db.scalar(select(func.count()).select_from(PersonOrm)) or 0
        result = await db.execute(
            select(PersonOrm).order_by(PersonOrm.id.desc()).limit(20)
        )
        rows = result.scalars().all()
        data = [
            {
                "id":          r.id,
                "passengerId": int(r.passenger_id) if r.passenger_id and r.passenger_id.strip().isdigit() else r.id,
                "survived":    int(r.survived)     if r.survived     and r.survived.strip().isdigit()     else 0,
                "pclass":      int(r.pclass)       if r.pclass       and r.pclass.strip().isdigit()       else 0,
                "name":        r.name     or "",
                "gender":      "male" if r.gender and r.gender.strip().lower() in ("male", "m") else "female",
                "age":         float(r.age) if r.age and r.age.strip().replace(".", "", 1).isdigit() else None,
                "fare":        float(r.fare) if r.fare and r.fare.strip().replace(".", "", 1).isdigit() else None,
                "embarked":    r.embarked or "",
            }
            for r in rows
        ]
        return {"data": data, "total": total}
    except Exception:
        return {"data": [], "total": 0}


@admin_stats_router.get("/intent-logs")
async def get_admin_intent_logs():
    # intent_logs 테이블 없음
    return {"data": [], "total": 0}

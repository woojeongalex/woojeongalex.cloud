"""Neon 테이블·INSERT 연동 점검: python scripts/check_neon_music.py"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

TABLES = (
    "users",
    "sing_evaluations",
    "user_vocal_recordings",
    "ai_vocal_analyses",
    "vocal_recommendations",
    "instrument_evaluations",
    "instrument_recordings",
    "instrument_tuning_analyses",
    "speech_evaluations",
    "speech_recordings",
    "speech_feedback_analyses",
)


async def main() -> int:
    if not os.getenv("DATABASE_URL"):
        print("FAIL: DATABASE_URL 없음 (backend/.env)")
        return 1

    from sqlalchemy import text

    import friday13th.adapter.outbound.orm.user_model  # noqa: F401
    import music.adapter.outbound.orm.instrument_evaluation_model  # noqa: F401
    import music.adapter.outbound.orm.instrument_recording_model  # noqa: F401
    import music.adapter.outbound.orm.instrument_tuning_analysis_model  # noqa: F401
    import music.adapter.outbound.orm.speech_evaluation_model  # noqa: F401
    import music.adapter.outbound.orm.speech_recording_model  # noqa: F401
    import music.adapter.outbound.orm.speech_feedback_analysis_model  # noqa: F401
    from database import dispose_engine, get_session_factory, init_db
    from music.adapter.inbound.api.schemas.instrument_schemas import (
        InstrumentEvaluationCreateRequest,
    )
    from music.adapter.inbound.api.schemas.speech_schemas import SpeechEvaluationCreateRequest
    from music.adapter.inbound.api.mappers.music_inbound_mapper import (
        from_instrument_create,
        from_speech_create,
    )
    from music.adapter.outbound.pg.instrument_pg_repository import InstrumentPgRepository
    from music.adapter.outbound.pg.speech_pg_repository import SpeechPgRepository
    from music.app.use_cases.instrument_interactor import InstrumentInteractor
    from music.app.use_cases.speech_interactor import SpeechInteractor

    await init_db()
    factory = get_session_factory()
    missing = []

    async with factory() as session:
        for name in TABLES:
            ok = (
                await session.execute(
                    text(
                        "SELECT EXISTS ("
                        " SELECT 1 FROM information_schema.tables"
                        " WHERE table_schema='public' AND table_name=:n)"
                    ),
                    {"n": name},
                )
            ).scalar()
            print(f"table {name}: {'OK' if ok else 'MISSING'}")
            if not ok:
                missing.append(name)

        if missing:
            await dispose_engine()
            return 1

        inst_id = (
            await InstrumentInteractor(
                InstrumentPgRepository(session=session)
            ).upload(
                from_instrument_create(
                    InstrumentEvaluationCreateRequest(
                        instrumentId="guitar",
                        tuningAccuracy=90,
                        pitchDeviationCents=4,
                        summary="integration check",
                        stringReadings=[{"label": "E2", "cents": 2}],
                        fileName="check.webm",
                        durationSec=2,
                    )
                )
            )
        ).id
        speech_id = (
            await SpeechInteractor(
                SpeechPgRepository(session=session)
            ).upload(
                from_speech_create(
                    SpeechEvaluationCreateRequest(
                        topicId="daily",
                        clarityScore=85,
                        paceScore=83,
                        toneScore=84,
                        summary="integration check",
                        feedbackPoints=["test"],
                        fileName="check.webm",
                        durationSec=2,
                    )
                )
            )
        ).id
        print(f"insert instrument_evaluations.id={inst_id}")
        print(f"insert speech_evaluations.id={speech_id}")

        await session.execute(
            text("DELETE FROM instrument_evaluations WHERE id = :id"),
            {"id": inst_id},
        )
        await session.execute(
            text("DELETE FROM speech_evaluations WHERE id = :id"),
            {"id": speech_id},
        )
        await session.commit()
        print("cleanup: OK")

    await dispose_engine()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

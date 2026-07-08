import logging
import sys


def configure_logging() -> None:
    """터미널에 friday13th·main 로그가 보이도록 설정합니다."""
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    stream_handlers = [h for h in root.handlers if isinstance(h, logging.StreamHandler)]
    if stream_handlers:
        for stream_handler in stream_handlers:
            stream_handler.setFormatter(formatter)
    else:
        root.addHandler(handler)

    for name in (
        "main",
        "database",
        "friday13th",
        "friday13th.adapter.inbound.api.v1.signup_router",
        "friday13th.adapter.inbound.api.v1.login_router",
        "friday13th.app.use_cases.signup_interactor",
        "friday13th.app.use_cases.login_interactor",
        "friday13th.adapter.outbound.pg.login_pg_repository",
        "friday13th.adapter.outbound.pg.signup_pg_repository",
        "music",
        "music.adapter.inbound.api.v1.search_router",
        "music.adapter.inbound.api.v1.evaluation_router",
        "music.adapter.inbound.api.v1.suggest_router",
        "music.adapter.inbound.api.v1.instrument_router",
        "music.adapter.inbound.api.v1.speech_router",
        "music.adapter.inbound.api.v1.video_router",
        "music.app.use_cases.search_interactor",
        "music.adapter.outbound.pg.list_pg_repository",
        "music.app.use_cases.video_audio_preprocess",
        "music.app.use_cases.librosa_vocal_analysis",
        "music.app.use_cases.emotion_analysis",
        "music.app.use_cases.video_analysis_interactor",
        "music.app.use_cases.evaluation_interactor",
        "music.app.use_cases.suggest_interactor",
        "music.app.use_cases.instrument_interactor",
        "music.app.use_cases.speech_interactor",
        "music.app.use_cases.sing_service",
        "music.adapter.outbound.pg.sing_pg_repository",
        "titanic",
        "titanic.app.titanic_flow_log",
        "titanic.adapter.inbound.api.parsers.titanic_csv_parser",
        "titanic.adapter.inbound.api.handlers.db_error_handler",
        "titanic.adapter.inbound.api.handlers.titanic_inbound_handlers",
        "titanic.adapter.inbound.api.v1.james_router",
        "titanic.app.factories.titanic_use_case_factory",
        "titanic.adapter.outbound.factories.pg_titanic_use_case_factory",
        "titanic.app.use_cases.james_interactor",
        "titanic.adapter.outbound.pg.james_pg_repository",
        "titanic.adapter.inbound.api.v1.walter_router",
        "titanic.app.use_cases.walter_interactor",
        "titanic.adapter.outbound.pg.walter_pg_repository",
    ):
        pkg_logger = logging.getLogger(name)
        pkg_logger.setLevel(logging.INFO)
        pkg_logger.propagate = True

    access_logger = logging.getLogger("uvicorn.access")
    access_logger.setLevel(logging.INFO)

    class _HealthFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            msg = record.getMessage()
            return "/health" not in msg

    access_logger.addFilter(_HealthFilter())

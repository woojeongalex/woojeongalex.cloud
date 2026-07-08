"""타이타닉 요청 흐름 로그 — 실행 레이어만 (inbound → usecase → outbound).

ports/input · ports/output 은 추상 계약(ABC)이라 런타임·로그 대상이 아니다.
"""

import logging

logger = logging.getLogger(__name__)

FLOW_LAYERS = ("inbound", "usecase", "outbound")


def _source_file_clause(source_file: str | None) -> str:
    if source_file is None:
        return ""
    label = source_file.strip() if source_file and source_file.strip() else "latest"
    return f"source_file={label} | "


def titanic_flow_log(
    flow: str,
    layer: str,
    message: str,
    *args: object,
    source_file: str | None = None,
) -> None:
    if layer not in FLOW_LAYERS:
        raise ValueError(
            f"flow log layer must be one of {FLOW_LAYERS}, got {layer!r} "
            "(abstract ports input/output are not logged)"
        )
    file_clause = _source_file_clause(source_file)
    logger.info(
        "[TITANIC-FLOW][%s][%s] %s" + message,
        flow,
        layer,
        file_clause,
        *args,
    )

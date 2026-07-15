from fastapi import Depends

from silicon_valley.app.ports.input.piper_hendricks__ceo_use_case import (
    HendricksCeoUseCase,
)
from silicon_valley.app.ports.input.semantic_router_use_case import (
    SemanticRouterUseCase,
)
from silicon_valley.app.ports.output.gemini_port import GeminiPort
from silicon_valley.app.use_cases.semantic_router_interactor import (
    SemanticRouterInteractor,
)
from silicon_valley.dependencies.gemini_provider import get_gemini_client
from silicon_valley.dependencies.piper_hendricks__ceo_provider import (
    get_hendricks_ceo_use_case,
)


def get_semantic_router_use_case(
    hendricks: HendricksCeoUseCase = Depends(get_hendricks_ceo_use_case),
    gemini: GeminiPort = Depends(get_gemini_client),
) -> SemanticRouterUseCase:
    return SemanticRouterInteractor(hendricks=hendricks, gemini=gemini)

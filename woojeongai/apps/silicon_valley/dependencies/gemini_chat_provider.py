from fastapi import Depends

from silicon_valley.app.ports.input.gemini_chat_use_case import GeminiChatUseCase
from silicon_valley.app.ports.output.gemini_port import GeminiPort
from silicon_valley.app.use_cases.gemini_chat_interactor import GeminiChatInteractor
from silicon_valley.dependencies.gemini_provider import get_gemini_client


def get_gemini_chat_use_case(
    gemini: GeminiPort = Depends(get_gemini_client),
) -> GeminiChatUseCase:
    return GeminiChatInteractor(gemini=gemini)

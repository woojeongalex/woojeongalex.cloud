from fastapi import Depends

from core.matrix.keymaker_api import Keymaker, get_keymaker
from silicon_valley.adapter.outbound.gemini.gemini_client import GeminiClient
from silicon_valley.app.ports.output.gemini_port import GeminiPort


def get_gemini_client(keymaker: Keymaker = Depends(get_keymaker)) -> GeminiPort:
    return GeminiClient(keymaker=keymaker)

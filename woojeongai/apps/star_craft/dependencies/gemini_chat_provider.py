from fastapi import Depends

from core.matrix.keymaker_api import Keymaker, get_keymaker
from star_craft.adapter.outbound.nlp.gemini_chat_gateway import GeminiChatGateway
from star_craft.app.ports.output.gemini_chat_port import GeminiChatPort


def get_gemini_chat_gateway(
    keymaker: Keymaker = Depends(get_keymaker),
) -> GeminiChatPort:
    return GeminiChatGateway(keymaker=keymaker)

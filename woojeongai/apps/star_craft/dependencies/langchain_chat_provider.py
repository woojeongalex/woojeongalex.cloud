from fastapi import Depends

from core.matrix.keymaker_api import Keymaker, get_keymaker
from star_craft.adapter.outbound.repositories.langchain_chat_repository import (
    LangchainChatRepository,
)
from star_craft.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from star_craft.app.ports.output.langchain_chat_port import LangchainChatPort
from star_craft.app.use_cases.langchain_chat_interactor import LangchainChatInteractor


def get_langchain_chat_repository(
    keymaker: Keymaker = Depends(get_keymaker),
) -> LangchainChatPort:
    return LangchainChatRepository(keymaker=keymaker)


def get_langchain_chat_use_case(
    repository: LangchainChatPort = Depends(get_langchain_chat_repository),
) -> LangchainChatUseCase:
    return LangchainChatInteractor(repository=repository)

from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_gilfoyle_system_dto import GilfoyleSystemQuery, GilfoyleSystemResponse


class GilfoyleSystemPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: GilfoyleSystemQuery) -> GilfoyleSystemResponse:
        '''버트람 길포일의 자기 소개 레포지토리 추상 메소드'''
        pass

from __future__ import annotations

from abc import ABC, abstractmethod


class KeywordParserPort(ABC):
    @abstractmethod
    def extract_keyword(self, command: str) -> str:
        """자연어 명령에서 검색할 핵심 키워드를 추출한다."""
        pass

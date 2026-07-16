from fastapi import Depends

from core.matrix.keymaker_api import Keymaker, get_keymaker
from star_craft.adapter.outbound.nlp.gemini_keyword_parser import GeminiKeywordParser
from star_craft.app.ports.output.keyword_parser_port import KeywordParserPort


def get_keyword_parser(keymaker: Keymaker = Depends(get_keymaker)) -> KeywordParserPort:
    return GeminiKeywordParser(keymaker=keymaker)

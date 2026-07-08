"""[Layer: Domain] Franz 악기 튜닝 카탈로그 (인메모리 · DB 미저장)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstrumentCatalogItem:
    instrument_id: str
    label: str
    description: str
    standard_tuning: str


INSTRUMENT_CATALOG: tuple[InstrumentCatalogItem, ...] = (
    InstrumentCatalogItem(
        instrument_id="guitar",
        label="기타",
        description="6현 기타 표준 튜닝(E-A-D-G-B-E) 기준 음정·튜닝 점검",
        standard_tuning="E2 A2 D3 G3 B3 E4",
    ),
    InstrumentCatalogItem(
        instrument_id="piano",
        label="피아노",
        description="88건반 피아노 A4=440Hz 기준 음정·튜닝 점검",
        standard_tuning="A4=440Hz",
    ),
)


def search_instruments(q: str = "") -> list[InstrumentCatalogItem]:
    needle = q.strip().lower()
    if not needle:
        return list(INSTRUMENT_CATALOG)
    return [
        item
        for item in INSTRUMENT_CATALOG
        if needle in item.label.lower()
        or needle in item.instrument_id.lower()
        or needle in item.description.lower()
    ]

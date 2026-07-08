from pydantic import BaseModel, Field


class InstrumentCatalogHit(BaseModel):
    instrument_id: str
    label: str
    description: str
    standard_tuning: str


class InstrumentCatalogResponse(BaseModel):
    query: str = ""
    hits: list[InstrumentCatalogHit]
    count: int


class FranzIntroduceSchema(BaseModel):
    id: int = Field(0, description="Franz ID")
    name: str = Field("악기 프란츠", description="Franz's name")


class FranzIntroduceResponse(BaseModel):
    id: int
    name: str

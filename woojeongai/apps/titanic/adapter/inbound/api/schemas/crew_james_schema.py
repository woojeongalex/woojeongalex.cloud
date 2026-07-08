from typing import Optional

from pydantic import BaseModel, Field, model_validator

_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "passenger_id": ("passenger_id", "PassengerId"),
    "survived": ("survived", "Survived"),
    "pclass": ("pclass", "Pclass"),
    "name": ("name", "Name"),
    "gender": ("gender", "Sex"),
    "age": ("age", "Age"),
    "sib_sp": ("sib_sp", "SibSp"),
    "parch": ("parch", "Parch"),
    "ticket": ("ticket", "Ticket"),
    "fare": ("fare", "Fare"),
    "cabin": ("cabin", "Cabin"),
    "embarked": ("embarked", "Embarked"),
}

_OPTIONAL_COLUMNS: frozenset[str] = frozenset({"survived"})
JAMES_CSV_COLUMNS: tuple[str, ...] = tuple(
    col for col in _COLUMN_ALIASES if col not in _OPTIONAL_COLUMNS
)


def has_james_csv_column(col: str, headers: list[str]) -> bool:
    aliases = _COLUMN_ALIASES.get(col, (col,))
    return any(h in headers for h in aliases)


class JamesSchema(BaseModel):
    passenger_id: Optional[str] = Field(None)
    survived: Optional[str] = Field(None)
    pclass: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    gender: Optional[str] = Field(None)
    age: Optional[str] = Field(None)
    sib_sp: Optional[str] = Field(None)
    parch: Optional[str] = Field(None)
    ticket: Optional[str] = Field(None)
    fare: Optional[str] = Field(None)
    cabin: Optional[str] = Field(None)
    embarked: Optional[str] = Field(None)

    @model_validator(mode="before")
    @classmethod
    def normalize_csv_columns(cls, data: dict) -> dict:
        normalized = {}
        for field, aliases in _COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in data:
                    normalized[field] = data[alias]
                    break
        return normalized


class JamesUploadResponse(BaseModel):
    saved: int = Field(..., description="저장된 레코드 수")

from pydantic import BaseModel, ConfigDict, Field


class PassengerCsvRow(BaseModel):
    """CSV 1행 — 컬럼명은 Titanic 데이터셋 헤더와 동일."""

    model_config = ConfigDict(populate_by_name=True)

    passenger_id: str = Field(alias="PassengerId")
    survived: str = Field(alias="Survived")
    pclass: str = Field(alias="Pclass")
    name: str = Field(alias="Name")
    gender: str = Field(alias="Sex")
    age: str = Field(alias="Age")
    sib_sp: str = Field(alias="SibSp")
    parch: str = Field(alias="Parch")
    ticket: str = Field(alias="Ticket")
    fare: str = Field(alias="Fare")

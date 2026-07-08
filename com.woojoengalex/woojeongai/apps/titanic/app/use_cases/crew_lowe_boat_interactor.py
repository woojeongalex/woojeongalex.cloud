"""[Layer: Use Cases] Lowe boat (LoweBoatUseCase 구현)."""

import numpy as np
import pandas as pd

from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema
from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.output.crew_lowe_boat_port import LoweBoatPort

class LoweBoatInteractor(LoweBoatUseCase):
    def __init__(self, repository: LoweBoatPort) -> None:
        self.repository = repository

    def feature_engineering(self, train_set: pd.DataFrame, test_set: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list]:
        train = train_set.copy()
        test = test_set.copy()

        # 1. Label 분리
        y_label = pd.to_numeric(train["survived"], errors="coerce").fillna(0).astype(int).tolist()
        train = train.drop(columns=["survived"])

        # 2. 호칭 추출 및 Nominal 변환
        if "name" in train.columns:
            train["Title"] = train["name"].str.extract(r"([A-Za-z]+)\.", expand=False)
            train["Title"] = train["Title"].replace(
                ["Capt", "Col", "Don", "Dr", "Major", "Rev", "Jonkheer", "Dona", "Mme"], "Rare"
            )
            train["Title"] = train["Title"].replace(["Countess", "Lady", "Sir"], "Royal")
            train["Title"] = train["Title"].replace({"Mlle": "Mr", "Ms": "Miss"})
            title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Royal": 5, "Rare": 6}
            train["Title"] = train["Title"].map(title_mapping).fillna(0).astype(int)
        if "name" in test.columns:
            test["Title"] = test["name"].str.extract(r"([A-Za-z]+)\.", expand=False)
            test["Title"] = test["Title"].replace(
                ["Capt", "Col", "Don", "Dr", "Major", "Rev", "Jonkheer", "Dona", "Mme"], "Rare"
            )
            test["Title"] = test["Title"].replace(["Countess", "Lady", "Sir"], "Royal")
            test["Title"] = test["Title"].replace({"Mlle": "Mr", "Ms": "Miss"})
            title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Royal": 5, "Rare": 6}
            test["Title"] = test["Title"].map(title_mapping).fillna(0).astype(int)

        # 3. 가족 규모 파생 변수 (FamilySize, IsAlone)
        for df in [train, test]:
            sib = pd.to_numeric(df["sib_sp"], errors="coerce").fillna(0)
            par = pd.to_numeric(df["parch"], errors="coerce").fillna(0)
            df["FamilySize"] = (sib + par + 1).astype(int)
            df["IsAlone"] = (df["FamilySize"] == 1).astype(int)

        # 5. 성별 Nominal 변환 (female=1, male=0)
        train["gender"] = train["gender"].map({"male": 0, "female": 1}).fillna(0).astype(int)
        if "gender" in test.columns:
            test["gender"] = test["gender"].map({"male": 0, "female": 1}).fillna(0).astype(int)

        # 6. 나이 구간 Ordinal 변환 및 결측치 처리
        bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
        age_labels = ["Unknown", "Baby", "Child", "Teenager", "Student", "Young Adult", "Adult", "Senior"]
        age_title_mapping = {
            0: "Unknown", 1: "Baby", 2: "Child", 3: "Teenager",
            4: "Student", 5: "Young Adult", 6: "Adult", 7: "Senior",
        }
        age_mapping = {v: k for k, v in age_title_mapping.items()}
        for df in [train, test]:
            if "age" in df.columns:
                df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(-0.5)
                df["AgeGroup"] = pd.cut(df["age"], bins, labels=age_labels).astype(str)
                if "Title" in df.columns:
                    mask = df["AgeGroup"] == "Unknown"
                    df.loc[mask, "AgeGroup"] = df.loc[mask, "Title"].map(age_title_mapping)
                df["AgeGroup"] = pd.to_numeric(df["AgeGroup"].map(age_mapping), errors="coerce").fillna(0).astype(int)

        # 7. 승선항 Nominal 변환
        for df in [train, test]:
            if "embarked" in df.columns:
                df["embarked"] = pd.to_numeric(
                    df["embarked"].fillna("S").map({"S": 1, "C": 2, "Q": 3}), errors="coerce"
                ).fillna(1).astype(int)

        # 8. 요금 Ordinal 변환
        for df in [train, test]:
            if "fare" in df.columns:
                df["fare"] = pd.to_numeric(df["fare"], errors="coerce").fillna(0)
                _fare_cut = pd.qcut(df["fare"], 4, duplicates="drop")
                _n = len(_fare_cut.cat.categories)
                df["FareBand"] = (
                    pd.qcut(df["fare"], 4, labels=list(range(1, _n + 1)), duplicates="drop")
                    .astype(float).fillna(1).astype(int)
                )

        # 9. 불필요 컬럼 드롭
        drop_cols = ["name", "age", "fare", "ticket", "cabin", "passenger_id", "source_file", "id", "created_at"]
        train = train.drop(columns=[c for c in drop_cols if c in train.columns])
        test = test.drop(columns=[c for c in drop_cols if c in test.columns])

        return train, test, y_label

    async def introduce_myself(self, schema: LoweBoatSchema) -> LoweBoatResponse:
        return await self.repository.introduce_myself(LoweBoatQuery(
            id=schema.id,
            name=schema.name,
        ))


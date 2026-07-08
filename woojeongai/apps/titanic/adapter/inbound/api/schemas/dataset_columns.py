"""타이타닉 생존 예측 데이터셋 컬럼 정의 (학습·API 문서용)."""

from typing import TypedDict


class ColumnSpec(TypedDict):
    name: str
    description: str
    dtype: str
    notes: str


TITANIC_COLUMN_SPECS: tuple[ColumnSpec, ...] = (
    {
        "name": "Survived",
        "description": "생존 여부",
        "dtype": "int",
        "notes": "0 = 사망, 1 = 생존 (예측 타깃)",
    },
    {
        "name": "Pclass",
        "description": "티켓 클래스",
        "dtype": "int",
        "notes": "1 = 1등석, 2 = 2등석, 3 = 3등석",
    },
    {
        "name": "Sex",
        "description": "성별",
        "dtype": "str",
        "notes": "male | female",
    },
    {
        "name": "Age",
        "description": "나이",
        "dtype": "float",
        "notes": "결측 가능 — 학습 시 중앙값 대체",
    },
    {
        "name": "SibSp",
        "description": "함께 탑승한 형제자매·배우자 수",
        "dtype": "int",
        "notes": "",
    },
    {
        "name": "Parch",
        "description": "함께 탑승한 부모·자녀 수",
        "dtype": "int",
        "notes": "",
    },
    {
        "name": "Ticket",
        "description": "티켓 번호",
        "dtype": "str",
        "notes": "",
    },
    {
        "name": "Fare",
        "description": "탑승 요금",
        "dtype": "float",
        "notes": "결측 가능 — 학습 시 중앙값 대체",
    },
    {
        "name": "Cabin",
        "description": "객실(수하물) 번호",
        "dtype": "str",
        "notes": "결측 다수",
    },
    {
        "name": "Boat",
        "description": "탈출 보트 번호",
        "dtype": "str",
        "notes": "생존·구조 시 기록 (원본 CSV에 없을 수 있음)",
    },
    {
        "name": "Embarked",
        "description": "승선 항구",
        "dtype": "str",
        "notes": "C = Cherbourg, Q = Queenstown, S = Southampton",
    },
)

# 저장소 CSV에만 있는 식별·이름 컬럼
EXTRA_CSV_COLUMNS: tuple[ColumnSpec, ...] = (
    {
        "name": "PassengerId",
        "description": "승객 ID",
        "dtype": "int",
        "notes": "행 식별자",
    },
    {
        "name": "Name",
        "description": "승객 이름",
        "dtype": "str",
        "notes": "",
    },
)

# 결정 트리 학습에 사용하는 피처 (ML 스키마 문서용)
ML_FEATURE_COLUMNS: tuple[str, ...] = ("Pclass", "Sex", "Age", "Fare")
ML_TARGET_COLUMN: str = "Survived"

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from titanic.adapter.outbound.orm.passenger_rose_model_strategies import build_all_strategies
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.passenger_jack_trainer_port import JackTrainerPort

logger = logging.getLogger("titanic_flow_log")

# 알고리즘 10종 훈련 매니페스트 (titanic-algorithm.md 기반)
_MODEL_MANIFEST: list[dict[str, Any]] = [
    {
        "rank": 1,
        "name": "XGBoost",
        "strategy_class": "XGBoostStrategy",
        "type": "gradient_boosting",
        "preprocessing": "standardization",
        "hyperparameters": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 6,
                            "reg_alpha": 0.1, "reg_lambda": 1.0},
        "note": "규제(Regularization)로 과적합 방지. 리더보드 최상위권 필수.",
    },
    {
        "rank": 2,
        "name": "RandomForest",
        "strategy_class": "RandomForestStrategy",
        "type": "bagging",
        "preprocessing": "none",
        "hyperparameters": {"n_estimators": 200, "max_depth": 8, "min_samples_split": 4},
        "note": "튜닝 없이도 안정적인 Baseline. 데이터 노이즈에 강함.",
    },
    {
        "rank": 3,
        "name": "LightGBM",
        "strategy_class": "LightGBMStrategy",
        "type": "gradient_boosting",
        "preprocessing": "standardization",
        "hyperparameters": {"num_leaves": 31, "learning_rate": 0.05, "n_estimators": 200},
        "note": "리프 중심 분할. 대용량에 특화, 피처 조합 실험에 유용.",
    },
    {
        "rank": 4,
        "name": "CatBoost",
        "strategy_class": "CatBoostStrategy",
        "type": "gradient_boosting",
        "preprocessing": "none",
        "hyperparameters": {"iterations": 500, "depth": 6, "learning_rate": 0.03},
        "note": "범주형(Sex, Embarked) 별도 인코딩 불필요. 타이타닉 최적.",
    },
    {
        "rank": 5,
        "name": "LogisticRegression",
        "strategy_class": "LogisticRegressionStrategy",
        "type": "linear",
        "preprocessing": "standardization",
        "hyperparameters": {"C": 1.0, "max_iter": 200, "solver": "lbfgs"},
        "note": "피처별 영향력 직관적 해석 가능. Baseline 모델로 먼저 적용.",
    },
    {
        "rank": 6,
        "name": "DecisionTree",
        "strategy_class": "DecisionTreeStrategy",
        "type": "tree",
        "preprocessing": "none",
        "hyperparameters": {"max_depth": 5, "min_samples_leaf": 10, "criterion": "gini"},
        "note": "분류 기준 시각화에 유리. 과적합 위험 → max_depth 제한 필수.",
    },
    {
        "rank": 7,
        "name": "SVM",
        "strategy_class": "SVMStrategy",
        "type": "margin_based",
        "preprocessing": "standardization",
        "hyperparameters": {"C": 1.0, "kernel": "rbf", "gamma": "scale"},
        "note": "표준화 필수. 비선형 관계 파악에 유리.",
    },
    {
        "rank": 8,
        "name": "KNN",
        "strategy_class": "KNNStrategy",
        "type": "instance_based",
        "preprocessing": "normalization",
        "hyperparameters": {"n_neighbors": 7, "weights": "distance", "metric": "euclidean"},
        "note": "나이·요금·객실 기반 유사도. 정규화 필수.",
    },
    {
        "rank": 9,
        "name": "NaiveBayes",
        "strategy_class": "NaiveBayesStrategy",
        "type": "probabilistic",
        "preprocessing": "none",
        "hyperparameters": {"var_smoothing": 1e-9},
        "note": "특성 독립 가정. 계산 빠름. 희소 데이터에 준수한 성능.",
    },
    {
        "rank": 10,
        "name": "KMeans_PCA",
        "strategy_class": "KMeansPCAStrategy",
        "type": "unsupervised",
        "preprocessing": "standardization",
        "hyperparameters": {"kmeans": {"n_clusters": 3}, "pca": {"n_components": 5}},
        "note": "군집화·차원 축소로 파생 피처 생성. 보조 전처리 용도.",
    },
]

_PREPROCESSING_GUIDE: dict[str, str] = {
    "standardization": "이상치(Outlier) 존재 시 — 평균 0, 표준편차 1로 변환",
    "normalization":   "이상치 없고 분포 균일 시 — 0~1 범위 Min-Max 압축",
}

_FEATURE_ENGINEERING: list[str] = [
    "Title 추출: Name에서 Mr/Miss/Master/Mrs 파싱 → 사회적 지위·성별 보완",
    "FamilySize: SibSp + Parch + 1",
    "IsAlone: FamilySize == 1 이면 1",
    "AgeBinning: 유아(0-12) / 청소년(13-17) / 청년(18-35) / 장년(36-60) / 노년(61+)",
]

_ENSEMBLE_GUIDE: dict[str, str] = {
    "soft_voting": "XGBoost + RandomForest + LightGBM 예측 확률 평균",
    "stacking":    "개별 모델 예측값을 메타 모델 입력으로 재학습",
}


class JackTrainerInteractor(JackTrainerUseCase):
    def __init__(self, repository: JackTrainerPort):
        self.repository = repository

    async def get_model_train(self) -> dict[str, Any]:
        logger.info("[JackTrainerInteractor] get_model_train 진입")
        return {
            "models": _MODEL_MANIFEST,
            "preprocessing": _PREPROCESSING_GUIDE,
            "feature_engineering": _FEATURE_ENGINEERING,
            "ensemble": _ENSEMBLE_GUIDE,
        }

    async def train_model(self, train_set: pd.DataFrame) -> dict[str, Any]:
        '''로즈가 제안한 모델들을 훈련시키는 메소드'''
        logger.info("[JackTrainerInteractor] 학습 파이프라인 시작")

        train = train_set.copy()

        # survived 레이블 분리
        if "survived" in train.columns:
            y_label = pd.to_numeric(train.pop("survived"), errors="coerce").fillna(0).astype(int).tolist()
        else:
            y_label = [0] * len(train)

        # 불필요 컬럼 드롭
        drop_cols = ["name", "age", "fare", "ticket", "cabin", "passenger_id", "source_file", "id", "created_at"]
        train = train.drop(columns=[c for c in drop_cols if c in train.columns])

        # 남은 string 컬럼 강제 숫자 변환 (안전망)
        for col in train.columns:
            train[col] = pd.to_numeric(train[col], errors="coerce").fillna(0)

        X_train: list[list[float]] = train.values.tolist()

        # 로즈의 10개 전략으로 학습
        self._trained_strategies = {}
        trained_names = []
        for key, StrategyClass in build_all_strategies().items():
            strategy = StrategyClass()
            try:
                strategy.fit(X_train, y_label)
                self._trained_strategies[key] = strategy
                trained_names.append(strategy.name)
                logger.info(f"[JackTrainerInteractor] {strategy.name} 학습 완료")
            except Exception as e:
                logger.warning(f"[JackTrainerInteractor] {key} 학습 실패 | error={e}")

        return {
            "train_samples": len(X_train),
            "trained_models": trained_names,
            "trained_strategies": self._trained_strategies,
        }

    async def introduce_myself(self, request) -> JackTrainerResponse:
        return await self.repository.introduce_myself(JackTrainerQuery(
            id=request.id,
            name=request.name,
        ))

from __future__ import annotations

import logging
import math
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelSchema
from titanic.adapter.outbound.orm.passenger_rose_model_strategies import build_all_strategies
from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse
from titanic.app.ports.input.passenger_rose_model_use_case import PredictionStrategy, RoseModelUseCase
from titanic.app.ports.output.passenger_rose_model_port import RoseModelPort

logger = logging.getLogger("titanic_flow_log")

_HIGH = frozenset({"여성", "아이", "어린이", "구조", "생존", "탈출", "구명", "1등석", "부유"})
_LOW  = frozenset({"남성", "침몰", "사망", "익사", "죽음", "3등석", "빈곤"})


def _signals(keywords: list[str]) -> tuple[int, int]:
    kw = set(keywords)
    return len(kw & _HIGH), len(kw & _LOW)


# ── 1. XGBoost ──────────────────────────────────────────────────────────────
class XGBoostStrategy:
    """그래디언트 부스팅: 가중 점수 + 정규화."""

    def predict(self, keywords: list[str]) -> float:
        pos, neg = _signals(keywords)
        score = (pos * 1.5 - neg * 1.2) / max(len(keywords), 1)
        return min(max(0.5 + score * 0.2, 0.0), 1.0)


# ── 2. Random Forest ─────────────────────────────────────────────────────────
class RandomForestStrategy:
    """배깅: 서브셋 5개 다수결."""

    _SURVIVAL_TREES = [
        frozenset({"여성", "구조", "생존"}),
        frozenset({"아이", "탈출", "구명"}),
        frozenset({"1등석", "부유"}),
    ]
    _DEATH_TREES = [
        frozenset({"남성", "침몰", "사망"}),
        frozenset({"3등석", "죽음", "익사"}),
    ]

    def predict(self, keywords: list[str]) -> float:
        kw = set(keywords)
        votes = [1 for t in self._SURVIVAL_TREES if kw & t]
        votes += [0 for t in self._DEATH_TREES if kw & t]
        return sum(votes) / len(votes) if votes else 0.50


# ── 3. LightGBM ──────────────────────────────────────────────────────────────
class LightGBMStrategy:
    """리프 중심: 가장 구체적으로 매칭되는 키워드 우선."""

    _LEAF: dict[str, float] = {
        "여성": 0.74, "아이": 0.71, "1등석": 0.63,
        "남성": 0.21, "3등석": 0.24, "침몰": 0.18,
    }

    def predict(self, keywords: list[str]) -> float:
        scores = [self._LEAF[k] for k in keywords if k in self._LEAF]
        return max(scores) if scores else 0.50


# ── 4. CatBoost ──────────────────────────────────────────────────────────────
class CatBoostStrategy:
    """범주형 최적화: 인코딩 없이 범주 매핑 직접 적용."""

    _CAT: dict[str, float] = {
        "여성": 0.74, "남성": 0.19,
        "1등석": 0.63, "2등석": 0.47, "3등석": 0.24,
        "아이": 0.71, "성인": 0.38, "노인": 0.28,
    }

    def predict(self, keywords: list[str]) -> float:
        scores = [self._CAT[k] for k in keywords if k in self._CAT]
        return sum(scores) / len(scores) if scores else 0.50


# ── 5. Logistic Regression ───────────────────────────────────────────────────
class LogisticRegressionStrategy:
    """선형 가중합 → 시그모이드."""

    _WEIGHTS: dict[str, float] = {
        "여성": 2.1, "아이": 1.8, "구명": 1.5, "1등석": 1.2,
        "남성": -1.9, "3등석": -1.3, "침몰": -2.0, "사망": -2.5,
    }

    def predict(self, keywords: list[str]) -> float:
        z = sum(self._WEIGHTS.get(k, 0.0) for k in keywords)
        return 1.0 / (1.0 + math.exp(-z))


# ── 6. Decision Tree ─────────────────────────────────────────────────────────
class DecisionTreeStrategy:
    """명시적 규칙 트리."""

    def predict(self, keywords: list[str]) -> float:
        kw = set(keywords)
        if "여성" in kw or "아이" in kw:
            return 0.74 if kw & {"1등석", "2등석"} else 0.50
        if "남성" in kw:
            return 0.11 if "3등석" in kw else 0.21
        return 0.50


# ── 7. SVM ───────────────────────────────────────────────────────────────────
class SVMStrategy:
    """마진 최대화: 결정 경계로부터의 거리."""

    def predict(self, keywords: list[str]) -> float:
        pos, neg = _signals(keywords)
        margin = (pos - neg) / max(pos + neg, 1)
        return min(max(0.5 + margin * 0.3, 0.0), 1.0)


# ── 8. KNN ───────────────────────────────────────────────────────────────────
class KNNStrategy:
    """최근접 이웃: 알려진 승객 프로파일과의 자카드 유사도."""

    _PROFILES: list[tuple[frozenset, float]] = [
        (frozenset({"여성", "1등석"}), 0.97),
        (frozenset({"아이", "2등석"}), 0.89),
        (frozenset({"남성", "선원"}), 0.22),
        (frozenset({"남성", "3등석"}), 0.13),
    ]

    def predict(self, keywords: list[str]) -> float:
        kw = set(keywords)
        best_sim, best_prob = 0.0, 0.50
        for profile, prob in self._PROFILES:
            union = len(profile | kw)
            sim = len(profile & kw) / union if union else 0.0
            if sim > best_sim:
                best_sim, best_prob = sim, prob
        return best_prob


# ── 9. Naive Bayes ───────────────────────────────────────────────────────────
class NaiveBayesStrategy:
    """베이즈 정리: P(생존|키워드) 반복 갱신."""

    _PRIOR = 0.384  # 타이타닉 실제 생존율
    _LIKELIHOOD: dict[str, float] = {
        "여성": 3.8, "아이": 3.2, "1등석": 2.1,
        "남성": 0.21, "3등석": 0.48, "침몰": 0.30,
    }

    def predict(self, keywords: list[str]) -> float:
        p = self._PRIOR
        for k in keywords:
            lr = self._LIKELIHOOD.get(k, 1.0)
            p = (p * lr) / (p * lr + (1 - p))
        return round(p, 4)


# ── 10. K-Means & PCA ────────────────────────────────────────────────────────
class KMeansPCAStrategy:
    """군집 배정: 키워드를 생존/사망/중립 클러스터에 매핑."""

    _CLUSTER_PROB = {"고생존군": 0.78, "저생존군": 0.17, "중립군": 0.45}
    _RULES = [
        (frozenset({"여성", "아이", "1등석", "부유"}), "고생존군"),
        (frozenset({"남성", "3등석", "빈곤"}),          "저생존군"),
    ]

    def predict(self, keywords: list[str]) -> float:
        kw = set(keywords)
        for signals, cluster in self._RULES:
            if kw & signals:
                return self._CLUSTER_PROB[cluster]
        return self._CLUSTER_PROB["중립군"]


_STRATEGIES: dict[str, PredictionStrategy] = {
    "XGBoost":           XGBoostStrategy(),
    "RandomForest":      RandomForestStrategy(),
    "LightGBM":          LightGBMStrategy(),
    "CatBoost":          CatBoostStrategy(),
    "LogisticRegression": LogisticRegressionStrategy(),
    "DecisionTree":      DecisionTreeStrategy(),
    "SVM":               SVMStrategy(),
    "KNN":               KNNStrategy(),
    "NaiveBayes":        NaiveBayesStrategy(),
    "KMeans_PCA":        KMeansPCAStrategy(),
}

# DataFrame 행 → 한국어 키워드 변환 (Rose 전략 입력 형식)
def _row_to_keywords(row: pd.Series) -> list[str]:
    keywords: list[str] = []

    gender = str(row.get("gender", "")).lower()
    if gender == "female":
        keywords.append("여성")
    elif gender == "male":
        keywords.append("남성")

    try:
        pclass = int(row.get("pclass", 0))
        if pclass == 1:
            keywords.append("1등석")
        elif pclass == 2:
            keywords.append("2등석")
        elif pclass == 3:
            keywords.append("3등석")
    except (ValueError, TypeError):
        pass

    try:
        age = float(row.get("age", -1))
        if 0 <= age <= 12:
            keywords.append("아이")
        elif age > 60:
            keywords.append("노인")
        else:
            keywords.append("성인")
    except (ValueError, TypeError):
        pass

    try:
        fare = float(row.get("fare", 0))
        if fare > 50:
            keywords.append("부유")
        elif fare < 10:
            keywords.append("빈곤")
    except (ValueError, TypeError):
        pass

    return keywords


# ── Interactor ───────────────────────────────────────────────────────────────
class RoseModelInteractor(RoseModelUseCase):
    def __init__(
        self,
        repository: RoseModelPort,
        strategy: PredictionStrategy = RandomForestStrategy(),
    ) -> None:
        self.repository = repository
        self._strategy = strategy

    async def predict(self, keywords: list[str]) -> float:
        return self._strategy.predict(keywords)

    async def train_model(self, train_set: pd.DataFrame) -> dict[str, Any]:
        '''로즈의 10개 전략을 실제 훈련 데이터로 평가해 최적 전략을 선택하는 메소드'''
        logger.info("[RoseModelInteractor] 전략 평가 파이프라인 시작")

        train = train_set.copy()

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
            train["Title"] = pd.to_numeric(train["Title"].map(title_mapping), errors="coerce").fillna(0).astype(int)

        # 3. 성별 Nominal 변환 (female=1, male=0)
        train["gender"] = pd.to_numeric(train["gender"].map({"male": 0, "female": 1}), errors="coerce").fillna(0).astype(int)

        # 4. 나이 구간 Ordinal 변환 및 결측치 처리
        if "age" in train.columns:
            bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
            age_labels = ["Unknown", "Baby", "Child", "Teenager", "Student", "Young Adult", "Adult", "Senior"]
            age_title_mapping = {
                0: "Unknown", 1: "Baby", 2: "Child", 3: "Teenager",
                4: "Student", 5: "Young Adult", 6: "Adult", 7: "Senior",
            }
            age_mapping = {v: k for k, v in age_title_mapping.items()}
            train["age"] = pd.to_numeric(train["age"], errors="coerce").fillna(-0.5)
            train["AgeGroup"] = pd.cut(train["age"], bins, labels=age_labels).astype(str)
            if "Title" in train.columns:
                mask = train["AgeGroup"] == "Unknown"
                train.loc[mask, "AgeGroup"] = train.loc[mask, "Title"].map(age_title_mapping)
            train["AgeGroup"] = pd.to_numeric(train["AgeGroup"].map(age_mapping), errors="coerce").fillna(0).astype(int)

        # 5. 승선항 Nominal 변환
        if "embarked" in train.columns:
            train["embarked"] = pd.to_numeric(
                train["embarked"].fillna("S").map({"S": 1, "C": 2, "Q": 3}), errors="coerce"
            ).fillna(1).astype(int)

        # 6. 요금 Ordinal 변환
        if "fare" in train.columns:
            train["fare"] = pd.to_numeric(train["fare"], errors="coerce").fillna(0)
            _fare_cut = pd.qcut(train["fare"], 4, duplicates="drop")
            _n = len(_fare_cut.cat.categories)
            train["FareBand"] = (
                pd.qcut(train["fare"], 4, labels=list(range(1, _n + 1)), duplicates="drop")
                .astype(float).fillna(1).astype(int)
            )

        # 7. 불필요 컬럼 드롭
        drop_cols = ["name", "age", "fare", "ticket", "cabin", "passenger_id", "source_file", "id", "created_at"]
        train = train.drop(columns=[c for c in drop_cols if c in train.columns])

        # 남은 string 컬럼 강제 숫자 변환 (안전망)
        for col in train.columns:
            train[col] = pd.to_numeric(train[col], errors="coerce").fillna(0)

        X: list[list[float]] = train.values.tolist()

        # 검증 세트 20% 분리 (정확도는 검증 세트 기준)
        X_tr, X_val, y_tr, y_val = train_test_split(
            X, y_label, test_size=0.2, random_state=42
        )

        # 8. sklearn 10개 전략으로 학습 및 검증 세트 정확도 평가
        results: list[dict[str, Any]] = []
        best_name, best_acc = "RandomForest", 0.0
        self._trained_strategies: dict[str, Any] = {}

        for key, StrategyClass in build_all_strategies().items():
            strategy = StrategyClass()
            try:
                strategy.fit(X_tr, y_tr)                  # 80% 학습
                preds = strategy.predict(X_val)            # 20% 검증
                accuracy = sum(p == a for p, a in zip(preds, y_val)) / len(y_val)
                strategy.fit(X, y_label)                   # 예측용 전체 재학습
                self._trained_strategies[key] = strategy
                results.append({"name": strategy.name, "accuracy": round(accuracy, 4)})
                logger.info(f"[RoseModelInteractor] {strategy.name} val_accuracy={accuracy:.2%}")
                if accuracy > best_acc:
                    best_acc, best_name = accuracy, strategy.name
            except Exception as e:
                logger.warning(f"[RoseModelInteractor] {key} 평가 실패 | error={e}")

        logger.info(f"[RoseModelInteractor] 최적 전략 선택 완료 | strategy={best_name} accuracy={best_acc:.2%}")

        return {
            "train_samples": len(y_label),
            "strategies_evaluated": len(results),
            "results": sorted(results, key=lambda x: x["accuracy"], reverse=True),
            "selected_strategy": best_name,
            "selected_accuracy": round(best_acc, 4),
            "trained_strategies": self._trained_strategies,
        }

    def analyze_and_answer(  # noqa: C901
        self,
        intent: str,
        question: str,
        keywords: list[str],
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        survival_prob: float,
        best_strategy: str,
        best_accuracy: float,
    ) -> str:
        """질문 의도 + 키워드를 조합해 데이터프레임에서 정확한 통계를 조회해 반환한다.

        우선순위 체계
        ─────────────────────────────────────────────────────────────────────
        1. 이름 조회     — "이름"이 질문/키워드에 있으면 실제 이름 반환
        2. 등급별 종합   — "등급별" 또는 전체 클래스 비교 질문
        3. 성별 현황     — 여성/남성 키워드 (단독 or 조합)
        4. 단일 등급     — 1등석/2등석/3등석 + 생존 통계
        5. 평균 나이     — 나이/평균/연령 키워드
        6. 생존율/사망률 — 비율 조회
        7. 생존자 수     — "생존자" 키워드
        8. 사망자 수     — "사망자" 키워드 (원인 질문과 분리)
        9. 탑승항        — 출발항/항구 키워드
        10. intent 기반  — death·general·count 폴백
        ─────────────────────────────────────────────────────────────────────
        """
        # ── 기본 집계 (공통) ───────────────────────────────────────────────────
        total  = len(train_df) + len(test_df)
        s_col  = pd.to_numeric(train_df["survived"], errors="coerce").fillna(0) if "survived" in train_df.columns else pd.Series([0] * len(train_df))
        survived   = int(s_col.sum())
        death      = len(train_df) - survived
        surv_rate  = survived / total if total else 0
        kw         = set(keywords)

        # ── 1. 이름 조회 ───────────────────────────────────────────────────────
        if "이름" in question or kw & {"이름"}:
            if "name" not in train_df.columns:
                return "이름 데이터를 불러올 수 없습니다."
            if kw & {"사망자", "사망"} or "사망자" in question:
                names = train_df[s_col == 0]["name"].dropna().tolist()
                label, n = "사망자", len(names)
            else:
                names = train_df[s_col == 1]["name"].dropna().tolist()
                label, n = "생존자", len(names)
            sample = names[:5]
            return f"{label} 총 {n}명 중 대표 이름 5명:\n" + "\n".join(f"• {nm}" for nm in sample)

        # ── 2. 등급별 종합 분석 ────────────────────────────────────────────────
        if "등급별" in question or (kw & {"등급"} and any(w in question for w in ["현황", "비교", "각각", "각", "분포", "수는"])):
            if "pclass" in train_df.columns:
                lines = ["객실 등급별 탑승객 현황:"]
                for cls in [1, 2, 3]:
                    mask  = pd.to_numeric(train_df["pclass"], errors="coerce") == cls
                    cnt   = int(mask.sum())
                    s_cnt = int((mask & (s_col == 1)).sum())
                    rate  = s_cnt / cnt if cnt else 0
                    lines.append(f"• {cls}등석: 탑승 {cnt}명 / 생존 {s_cnt}명({rate:.1%}) / 사망 {cnt - s_cnt}명")
                return "\n".join(lines)

        # ── 3. 성별 현황 ───────────────────────────────────────────────────────
        has_female = bool(kw & {"여성", "여자", "여자분"} or "female" in question)
        has_male   = bool(kw & {"남성", "남자"} or "male" in question)

        if (has_female or has_male) and "gender" in train_df.columns:
            f_mask  = train_df["gender"] == "female"
            m_mask  = train_df["gender"] == "male"
            f_all   = int(f_mask.sum()) + (int((test_df["gender"] == "female").sum()) if "gender" in test_df.columns else 0)
            m_all   = int(m_mask.sum()) + (int((test_df["gender"] == "male").sum())   if "gender" in test_df.columns else 0)
            f_surv  = int((f_mask & (s_col == 1)).sum())
            m_surv  = survived - f_surv
            f_rate  = f_surv / f_all if f_all else 0
            m_rate  = m_surv / m_all if m_all else 0

            if has_female and has_male:
                return (
                    f"여성 탑승객 {f_all}명 중 생존 {f_surv}명({f_rate:.1%}), "
                    f"남성 탑승객 {m_all}명 중 생존 {m_surv}명({m_rate:.1%})입니다."
                )
            if has_female:
                return f"여성 탑승객은 총 {f_all}명이며, 그 중 {f_surv}명({f_rate:.1%})이 생존했습니다."
            return f"남성 탑승객은 총 {m_all}명이며, 그 중 {m_surv}명({m_rate:.1%})이 생존했습니다."

        # ── 4. 단일 등급 질문 ──────────────────────────────────────────────────
        if "pclass" in train_df.columns:
            for cls_num, cls_kw in [
                (1, {"1등석", "1등", "일등석", "퍼스트"}),
                (2, {"2등석", "2등", "이등석", "세컨드"}),
                (3, {"3등석", "3등", "삼등석", "서드"}),
            ]:
                if kw & cls_kw:
                    mask  = pd.to_numeric(train_df["pclass"], errors="coerce") == cls_num
                    cnt   = int(mask.sum())
                    s_cnt = int((mask & (s_col == 1)).sum())
                    rate  = s_cnt / cnt if cnt else 0
                    return f"{cls_num}등석 탑승객은 {cnt}명이며, 생존자는 {s_cnt}명({rate:.1%})입니다."

        # ── 5. 평균 나이 ───────────────────────────────────────────────────────
        if kw & {"나이", "평균", "연령"} and "age" in train_df.columns:
            avg = pd.to_numeric(train_df["age"], errors="coerce").mean()
            return f"탑승객 평균 나이는 약 {avg:.1f}세입니다."

        # ── 6. 생존율 · 사망률 ─────────────────────────────────────────────────
        if any(w in question for w in ["생존율", "생존률", "사망률", "사망율", "생존율이", "사망률이"]):
            return (
                f"타이타닉 전체 생존율 {surv_rate:.1%}({survived}명/{total}명), "
                f"사망률 {1 - surv_rate:.1%}({death}명/{total}명)."
            )

        # ── 7. 생존자 수 ───────────────────────────────────────────────────────
        if kw & {"생존자"} or "살아남" in question:
            return f"생존자는 총 {survived}명({surv_rate:.1%})입니다."

        # ── 8. 사망자 수 (원인·이유 질문과 분리) ──────────────────────────────
        if (kw & {"사망자"} or "사망자" in question) and not any(w in question for w in ["원인", "이유", "왜"]):
            return f"사망자는 총 {death}명({1 - surv_rate:.1%})입니다."

        # ── 9. 탑승항 ──────────────────────────────────────────────────────────
        if kw & {"출발", "항구", "탑승항", "승선항"} or any(w in question for w in ["출발항", "승선항", "어디서"]):
            if "embarked" in train_df.columns:
                port_map = {"S": "사우샘프턴(S)", "C": "쉘부르(C)", "Q": "퀸즈타운(Q)"}
                counts   = train_df["embarked"].fillna("S").map(port_map).value_counts()
                lines    = ["탑승항별 탑승객 수:"] + [f"• {p}: {n}명" for p, n in counts.items()]
                return "\n".join(lines)

        # ── 10. intent 기반 폴백 ───────────────────────────────────────────────
        if intent == "death":
            return (
                f"타이타닉(RMS Titanic)은 1912년 4월 14일 밤 북대서양에서 빙산과 충돌 후 침몰했습니다. "
                f"승객·선원 총 {total}명 중 {death}명(사망률 {1 - surv_rate:.1%})이 사망했으며, "
                f"{survived}명이 구명보트로 생존했습니다."
            )

        if intent == "general":
            return (
                f"RMS 타이타닉은 1912년 4월 10일 영국 사우샘프턴 출항, 4월 14일 빙산 충돌 후 침몰한 영국 여객선입니다. "
                f"총 탑승객 {total}명 — 생존자 {survived}명({surv_rate:.1%}), 사망자 {death}명({1 - surv_rate:.1%})."
            )

        # count / 기타 → 종합 통계
        return (
            f"타이타닉 총 탑승객 {total}명 — "
            f"생존자 {survived}명({surv_rate:.1%}), "
            f"사망자 {death}명({1 - surv_rate:.1%})."
        )

    async def introduce_myself(self, schema: RoseModelSchema) -> RoseModelResponse:
        return await self.repository.introduce_myself(RoseModelQuery(
            id=schema.id,
            name=schema.name,
        ))

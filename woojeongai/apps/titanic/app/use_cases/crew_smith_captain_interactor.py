"""[Layer: Use Cases] Smith captain (SmithCaptainUseCase 구현)."""
import base64
import logging
import re

import pandas as pd

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema, SmithCaptainSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTestUseCase
from titanic.app.ports.output.crew_smith_captain_port import SmithCaptainPort
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.input.crew_walter_use_case import WalterUseCase
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.input.crew_hartley_use_case import HartleyUseCase


logger = logging.getLogger("titanic_flow_log")

# 이 인텐트에만 sklearn ML 파이프라인을 가동한다 (유형 B)
_ML_INTENTS: frozenset[str] = frozenset({"personal", "importance"})

_FEATURE_KO: dict[str, str] = {
    "gender":     "성별",
    "pclass":     "객실 등급",
    "FareBand":   "요금 구간",
    "IsAlone":    "혼자 탑승 여부",
    "embarked":   "탑승 항구",
    "parch":      "부모/자녀 수",
    "AgeGroup":   "연령대",
    "sib_sp":     "형제/배우자 수",
    "FamilySize": "가족 규모",
}


def _importance_answer(train_df: pd.DataFrame, best_strategy: str, best_accuracy: float) -> str:
    numeric = train_df.select_dtypes(include="number")
    if "survived" not in numeric.columns:
        return "생존 데이터가 부족해 피처 중요도를 계산할 수 없습니다."

    corr = numeric.corr()["survived"].drop("survived")
    ranked = corr.abs().sort_values(ascending=False)

    lines = ["📊 생존율에 영향을 미치는 피처 순위 (상관계수 절대값 기준)\n"]
    for i, feat in enumerate(ranked.index, 1):
        val = corr[feat]
        ko = _FEATURE_KO.get(feat, feat)
        direction = "양(+)" if val > 0 else "음(-)"
        lines.append(f"{i}. {ko}({feat}): {val:+.2f}  [{direction} 상관관계]")

    top = ranked.index[0]
    lines.append(f"\n→ 생존율에 가장 중요한 요소는 '{_FEATURE_KO.get(top, top)}'입니다.")
    lines.append(f"적용 모델: {best_strategy}  정확도: {best_accuracy:.2%}")
    return "\n".join(lines)


def _personal_answer(
    question: str,
    rose_result: dict,
    train_df: pd.DataFrame,
    best_accuracy: float,
) -> str:
    # ── 나이 추출 ──────────────────────────────────────────────────────────────
    age_match = re.search(r"(\d{1,3})\s*(?:세|살)", question)
    age: int | None = int(age_match.group(1)) if age_match else None

    # ── 성별 추출 ──────────────────────────────────────────────────────────────
    is_female = any(w in question for w in ["여성", "여자", "여", "female"])
    gender_encoded = 1 if is_female else 0  # lowe FE: female=1, male=0

    # ── 객실 등급 추출 (언급 없으면 3등석 기본) ─────────────────────────────────
    if any(w in question for w in ["1등석", "1등", "일등석", "퍼스트"]):
        pclass = 1
    elif any(w in question for w in ["2등석", "2등", "이등석", "세컨드"]):
        pclass = 2
    else:
        pclass = 3

    # ── 나이 → AgeGroup 변환 (lowe FE 기준) ────────────────────────────────────
    def _age_to_group(a: int | None) -> int:
        if a is None:   return 0
        if a <= 0:      return 1   # Baby
        if a <= 5:      return 1
        if a <= 12:     return 2   # Child
        if a <= 18:     return 3   # Teenager
        if a <= 24:     return 4   # Student
        if a <= 35:     return 5   # Young Adult
        if a <= 60:     return 6   # Adult
        return 7                   # Senior

    # ── 기본 파생 피처 (혼자 탑승 가정) ─────────────────────────────────────────
    family_size = 1
    is_alone    = 1
    fare_band   = max(1, 5 - pclass)   # 1등석→4, 2등석→3, 3등석→2

    row_dict = {
        "pclass":     pclass,
        "gender":     gender_encoded,
        "sib_sp":     0,
        "parch":      0,
        "embarked":   1,            # Southampton 기본
        "FamilySize": family_size,
        "IsAlone":    is_alone,
        "AgeGroup":   _age_to_group(age),
        "FareBand":   fare_band,
    }

    feature_cols = [c for c in train_df.columns if c != "survived"]
    row = [row_dict.get(c, 0) for c in feature_cols]

    # ── 최적 훈련 전략으로 예측 ────────────────────────────────────────────────
    trained     = rose_result.get("trained_strategies", {})
    best_name   = rose_result.get("selected_strategy", "")
    prob: float = 0.5
    if best_name in trained:
        try:
            preds = trained[best_name].predict([row])
            prob  = float(preds[0])
        except Exception:
            pass

    gender_str = "여성" if is_female else "남성"
    age_str    = f"{age}세 " if age else ""
    verdict    = "생존했을 가능성이 높습니다 ✅" if prob >= 0.5 else "생존하지 못했을 가능성이 높습니다 ❌"

    return (
        f"[개인 생존 예측]\n"
        f"조건: {age_str}{gender_str} / {pclass}등석 / 혼자 탑승 / Southampton 출발\n"
        f"예측: {verdict}\n"
        f"생존 확률: {prob:.1%}  (모델: {best_name}, 정확도: {best_accuracy:.2%})\n"
        f"※ 미입력 항목(객실 등급·탑승항)은 가장 일반적인 조건으로 가정했습니다."
    )


class SmithCaptainInteractor(SmithCaptainUseCase):
    def __init__(
        self,
        repository: SmithCaptainPort,
        jack: JackTrainerUseCase,
        rose: RoseModelUseCase,
        cal: CalTestUseCase,
        walter: WalterUseCase,
        andrews: AndrewsArchitectUseCase,
        lowe: LoweBoatUseCase,
        hartley: HartleyUseCase,
    ):
        self.repository = repository
        self.jack = jack
        self.rose = rose
        self.cal = cal
        self.walter = walter
        self.andrews = andrews
        self.lowe = lowe
        self.hartley = hartley

    async def chat(self, schema: ChatSchema) -> SmithCaptainResponse:
        logger.info("[SmithCaptainInteractor] chat 진입 | messages=%s", schema.messages)

        # 1. Andrews: 질문 의도 분류
        question: dict = self.andrews.analyze_message_intent(schema.messages)
        intent:   str  = question["intent"]
        keywords: list = question["keywords"]

        # 2. Walter: 원본 데이터 로드 (survived 포함)
        raw_train_df: pd.DataFrame = await self.walter.get_train_set()
        raw_test_df:  pd.DataFrame = await self.walter.get_test_set()

        # ── [유형 B] ML 파이프라인 (personal · importance 인텐트에만) ──────────
        if intent in _ML_INTENTS:
            train_df_fe, _, y_label = self.lowe.feature_engineering(
                raw_train_df.copy(), raw_test_df.copy()
            )
            train_df_with_survived = train_df_fe.copy()
            train_df_with_survived["survived"] = y_label

            # Rose: sklearn 10개 모델 학습 + 검증 세트 정확도
            rose_result:   dict  = await self.rose.train_model(raw_train_df)
            best_strategy: str   = rose_result.get("selected_strategy", "없음")
            best_accuracy: float = rose_result.get("selected_accuracy", 0.0)

            # Jack: 모델 훈련 매니페스트
            await self.jack.train_model(train_df_with_survived)
            model_manifest: dict = await self.jack.get_model_train()

            # Cal: 점수 기반 최적 모델 선택
            test_result:   dict = await self.cal.test_models(model_manifest)
            top_cal_model: str  = test_result.get("top_model") or best_strategy

            if intent == "importance":
                answer = _importance_answer(train_df_with_survived, top_cal_model, best_accuracy)
            else:  # personal
                answer = _personal_answer(schema.messages, rose_result, train_df_fe, best_accuracy)

            graph: str | None = base64.b64encode(
                self.hartley.correlation_graph(train_df_with_survived)
            ).decode("utf-8")
            # [유형 B] PREDICTION — ML 검증 정확도 포함
            return SmithCaptainResponse(
                status="success",
                type="PREDICTION",
                message=answer,
                accuracy=best_accuracy,
                graph=graph,
            )

        # ── [유형 A] 통계 조회 — ML 없이 원본 데이터프레임 직접 집계 ──────────
        answer = self.rose.analyze_and_answer(
            intent=intent,
            question=schema.messages,
            keywords=keywords,
            train_df=raw_train_df,
            test_df=raw_test_df,
            survival_prob=0.0,
            best_strategy="",
            best_accuracy=0.0,
        )
        # [유형 A] STATISTICS — accuracy 필드 None (ML 미실행)
        return SmithCaptainResponse(
            status="success",
            type="STATISTICS",
            message=answer,
            accuracy=None,
            graph=None,
        )

    async def introduce_myself(self, schema: SmithCaptainSchema) -> SmithCaptainResponse:
        return await self.repository.introduce_myself(SmithCaptainQuery(
            id=schema.id,
            name=schema.name,
        ))


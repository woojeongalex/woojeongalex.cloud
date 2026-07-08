"""[Layer: Use Cases] Andrews architect — 의도 분류기 (하드룰 게이트 → ML 폴백).

분류 흐름:
    Stage 1 (STATISTICS 하드게이트)
        Kiwi 형태소에 집계·통계 트리거가 하나라도 존재하면 즉시 Label 0(count)로 단락.
        → ML predict() 절대 미실행 / accuracy=null 보장.

    Stage 2 (PREDICTION 하드게이트)
        Stage 1 통과 후, 개인 가정 조건 트리거가 있으면 즉시 Label 1(personal).

    Stage 3 (ML 폴백)
        importance·death·general 등 하드룰이 걸리지 않는 모호한 질문에만 사용.
        TF-IDF(1~2-gram) + LogisticRegression.
"""
from __future__ import annotations

from typing import cast

from kiwipiepy import Kiwi, Token
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectQuery, AndrewsArchitectResponse
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.output.crew_andrews_architect_port import AndrewsArchitectPort

_KEYWORD_TAGS: set[str] = {"NNG", "NNP", "SL", "VV", "VA"}

# ══════════════════════════════════════════════════════════════════════════════
# Stage 1 — STATISTICS 하드게이트
# "몇", "총", "평균" 등 집계·통계 지시어가 하나라도 있으면 무조건 Label 0(count).
# 이 게이트를 통과한 쿼리에는 ML predict()를 절대 호출하지 않는다.
# ══════════════════════════════════════════════════════════════════════════════
_STATS_GATE: frozenset[str] = frozenset({
    "몇",       # 몇 명, 몇 퍼센트
    "총",       # 총 탑승객, 총 생존자
    "개수",     # 개수가 얼마야
    "비율",     # 생존 비율
    "통계",     # 통계 알려줘
    "최대",     # 최대 나이
    "최소",     # 최소 요금
    "평균",     # 평균 나이
    "얼마",     # 얼마나 돼
    "퍼센트",   # 몇 퍼센트야
    "인원",     # 인원이 몇 명이야
    "합계",     # 합계
    "명",       # 명이야, 몇 명
    "율",       # 생존율이 어떻게 돼 → Kiwi가 생존+율로 분리 시 포착
    "률",       # 사망률, 생존률
    "분포",     # 나이 분포, 탑승객 분포
})

# ══════════════════════════════════════════════════════════════════════════════
# Stage 2 — PREDICTION 하드게이트
# Stage 1 통과 후, 개인 가정 조건 형태소가 있으면 Label 1(personal).
# "라면", "이라면", "만약" 등 가정·조건 어미 = 개인 예측 유스케이스 전용 신호.
# ══════════════════════════════════════════════════════════════════════════════
_PRED_GATE: frozenset[str] = frozenset({
    "라면",     # ~라면 살 수 있었을까
    "이라면",   # 여성이라면
    "만약",     # 만약 내가
    "한다면",   # 탑승한다면
    "이었다면", # 1등석이었다면
    "했다면",   # 탑승했다면
    "이면",     # 조건이면 — Kiwi가 EC 태그로 분리하는 경우 커버
})

# ══════════════════════════════════════════════════════════════════════════════
# Stage 3 — ML 폴백 훈련 말뭉치
# 하드룰이 걸리지 않는 중간 난이도 질문(importance, death, general)을 분류.
# ══════════════════════════════════════════════════════════════════════════════
_INTENT_CORPUS: list[tuple[str, str]] = [
    # importance — 피처 중요도·상관관계
    ("생존에 가장 중요한 요소가 뭐야", "importance"),
    ("어떤 피처가 생존율에 영향을 줘", "importance"),
    ("생존율과 상관관계가 높은 게 뭐야", "importance"),
    ("어떤 변수가 생존에 가장 큰 영향을 미쳐", "importance"),
    ("feature importance 알려줘", "importance"),
    ("생존을 결정하는 핵심 요인이 뭐야", "importance"),
    ("상관관계 분석 해줘", "importance"),
    ("피처 중요도 순위 알려줘", "importance"),
    ("생존율에 영향을 주는 변수는", "importance"),
    ("어떤 조건이 생존과 가장 관련 있어", "importance"),
    ("가장 중요한 변수를 순위별로 알려줘", "importance"),
    ("어떤 요인이 생존에 제일 중요해", "importance"),

    # death — 침몰 사건 정보
    ("타이타닉은 왜 침몰했어", "death"),
    ("침몰 당시 상황 알려줘", "death"),
    ("타이타닉 사망 원인이 뭐야", "death"),
    ("타이타닉 사고에 대해 알려줘", "death"),
    ("빙산 충돌 이야기 해줘", "death"),
    ("타이타닉 침몰 이유가 뭐야", "death"),
    ("타이타닉이 왜 가라앉았어", "death"),

    # personal — 하드룰 미검출 보완용 (가정 어미 변형)
    ("내 조건으로 생존 가능한지 알려줘", "personal"),
    ("2등석 30살 남성의 생존 확률", "personal"),
    ("어린아이의 생존 가능성은", "personal"),
    ("25세 여자 생존 확률 알려줘", "personal"),

    # count — 하드룰 미검출 보완용
    ("생존 비율이 어떻게 돼", "count"),
    ("탑승객 전체 인원 알려줘", "count"),
    ("각 등급별 탑승객 수는", "count"),
    ("생존률은 어떻게 돼", "count"),
    ("사망률이 어떻게 돼", "count"),

    # general
    ("타이타닉에 대해 알려줘", "general"),
    ("타이타닉이 뭐야", "general"),
    ("타이타닉 사건에 대해 설명해줘", "general"),
    ("안녕하세요", "general"),
    ("뭘 물어볼 수 있어", "general"),
    ("도움이 필요해", "general"),
]


def _kiwi_tokenize(kiwi: Kiwi, text: str) -> str:
    return " ".join(t.form for t in kiwi.tokenize(text))


class AndrewsArchitectInteractor(AndrewsArchitectUseCase):
    def __init__(self, repository: AndrewsArchitectPort) -> None:
        self.repository = repository
        self.kiwi = Kiwi()
        self._vectorizer, self._clf = self._fit_intent_classifier()

    def _fit_intent_classifier(self) -> tuple[TfidfVectorizer, LogisticRegression]:
        texts  = [_kiwi_tokenize(self.kiwi, t) for t, _ in _INTENT_CORPUS]
        labels = [label for _, label in _INTENT_CORPUS]
        vec    = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        clf    = LogisticRegression(C=1.0, max_iter=500, random_state=42)
        clf.fit(vec.fit_transform(texts), labels)
        return vec, clf

    def analyze_message_intent(self, user_messages: str) -> dict:
        tokens   = cast(list[Token], self.kiwi.tokenize(user_messages))
        keywords = [t.form for t in tokens if str(t.tag) in _KEYWORD_TAGS]
        forms    = {t.form for t in tokens}
        token_str = " ".join(t.form for t in tokens)

        # ── Stage 1: STATISTICS 하드게이트 ────────────────────────────────────
        # 집계·통계 트리거가 하나라도 검출되면 즉시 Label 0(count) 반환.
        # ML 분류기 진입 자체를 차단한다.
        if forms & _STATS_GATE:
            return {
                "keywords":   keywords,
                "intent":     "count",
                "confidence": 1.0,
                "tokens":     [{"form": t.form, "tag": str(t.tag)} for t in tokens],
            }

        # ── Stage 2: PREDICTION 하드게이트 ───────────────────────────────────
        # 개인 가정 조건 형태소가 있으면 즉시 Label 1(personal) 반환.
        if forms & _PRED_GATE:
            return {
                "keywords":   keywords,
                "intent":     "personal",
                "confidence": 1.0,
                "tokens":     [{"form": t.form, "tag": str(t.tag)} for t in tokens],
            }

        # ── Stage 3: ML 폴백 ─────────────────────────────────────────────────
        # importance·death·general 등 하드룰 미포착 케이스에만 도달.
        X_vec      = self._vectorizer.transform([token_str])
        proba      = self._clf.predict_proba(X_vec)[0]
        confidence = float(max(proba))
        intent     = str(self._clf.classes_[int(proba.argmax())]) if confidence >= 0.35 else "general"

        return {
            "keywords":   keywords,
            "intent":     intent,
            "confidence": round(confidence, 4),
            "tokens":     [{"form": t.form, "tag": str(t.tag)} for t in tokens],
        }

    async def introduce_myself(self, request) -> AndrewsArchitectResponse:
        return await self.repository.introduce_myself(AndrewsArchitectQuery(
            id=request.id,
            name=request.name,
        ))

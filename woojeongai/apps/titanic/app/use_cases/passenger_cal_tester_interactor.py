from __future__ import annotations

from dataclasses import dataclass

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTestSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTestQuery, CalTestResponse
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTestUseCase
from titanic.app.ports.output.passenger_cal_tester_port import CalTestPort


@dataclass(frozen=True)
class _ScoreRule:
    fit:       int  # 타이타닉 적합도 (0-40)
    balance:   int  # 복잡도 균형   (0-30)
    interpret: int  # 해석 가능성   (0-20)
    speed:     int  # 속도          (0-10)


_RULES: dict[str, _ScoreRule] = {
    "gradient_boosting": _ScoreRule(fit=40, balance=28, interpret=12, speed=7),
    "bagging":           _ScoreRule(fit=35, balance=30, interpret=15, speed=6),
    "tree":              _ScoreRule(fit=25, balance=25, interpret=20, speed=10),
    "linear":            _ScoreRule(fit=20, balance=30, interpret=18, speed=10),
    "margin_based":      _ScoreRule(fit=15, balance=20, interpret=8,  speed=5),
    "instance_based":    _ScoreRule(fit=12, balance=15, interpret=15, speed=3),
    "probabilistic":     _ScoreRule(fit=10, balance=28, interpret=16, speed=10),
    "unsupervised":      _ScoreRule(fit=5,  balance=10, interpret=5,  speed=8),
}

_DEFAULT_RULE = _ScoreRule(fit=5, balance=5, interpret=5, speed=5)


class CalTestInteractor(CalTestUseCase):
    def __init__(self, repository: CalTestPort):
        self.repository = repository

    async def evaluate_models(self, train_manifest: dict) -> dict:
        scored = []
        for model in train_manifest.get("models", []):
            rule  = _RULES.get(model["type"], _DEFAULT_RULE)
            total = rule.fit + rule.balance + rule.interpret + rule.speed
            scored.append({
                "name":           model["name"],
                "strategy_class": model["strategy_class"],
                "score":          total,
                "breakdown": {
                    "타이타닉_적합도": rule.fit,
                    "복잡도_균형":    rule.balance,
                    "해석_가능성":    rule.interpret,
                    "속도":          rule.speed,
                },
            })

        scored.sort(key=lambda m: m["score"], reverse=True)

        for placing, model in enumerate(scored, start=1):
            model["placing"] = placing

        return {
            "ranking": scored,
            "top_model": scored[0]["name"] if scored else None,
            "top3": [m["name"] for m in scored[:3]],
        }

    async def find_best_model(self, train_manifest: dict) -> dict:
        result = await self.evaluate_models(train_manifest)
        return result["ranking"][0] if result["ranking"] else {}

    async def introduce_myself(self, schema: CalTestSchema) -> CalTestResponse:
        return await self.repository.introduce_myself(CalTestQuery(
            id=schema.id,
            name=schema.name,
        ))

    async def test_models(self, test_set: dict) -> dict:
        '''칼이 로즈가 제안한 10개 모델의 트레이닝 정도를 점수화 해서 1등을 뽑는 것'''
        return await self.evaluate_models(test_set)
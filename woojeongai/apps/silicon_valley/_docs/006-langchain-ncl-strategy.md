# 006 — LangChain 전략: NCL 사례 (최적화된 여행 계획 제공)

> 참고 사례: NCL(Norwegian Cruise Line)은 LangChain의 맞춤형 프롬프팅·파인튜닝 기능을 활용해
> 고객 선호도와 탐색 기록 기반 실시간 맞춤 추천 AI 어시스턴트를 구축했다.
> 본 문서는 이 사례를 silicon_valley 앱에 적용하기 위한 구현 전략을 정의한다.
> 공통 행동 규칙은 [[003-langchain-harness]] 를 우선 따른다.

---

## 1. 사례 → silicon_valley 매핑

| NCL 사례 | silicon_valley 적용 대상 |
|----------|---------------------------|
| 고객 선호도 (좋아하는 목적지, 객실 타입 등) | 사용자 캐스팅 선호도 (선호 페르소나, 톤, 장르 등) |
| 탐색 기록 (browsing history) | 대화/조회 히스토리 (이전 캐스팅 요청, 조회한 인물 카드) |
| 실시간 변화하는 요구 대응 | 대화 도중 사용자가 조건을 바꿀 때 즉시 추천 갱신 |
| 맞춤형 여행 일정 추천 | 맞춤형 캐스팅 후보군 추천 |

핵심은 **"정적 추천"이 아니라 "선호도 프로필 + 실시간 컨텍스트"를 함께 반영하는 추천 체인**이다.

---

## 2. 아키텍처 (기존 클린 아키텍처 규칙 준수)

```
domain/
  entities/
    preference_profile.py        # 사용자 선호도 (누적 선호 태그, 가중치)
  value_objects/
    recommendation_criteria.py   # 이번 요청의 즉시 조건 (frozen)
app/
  dtos/
    recommend_command.py         # 입력 DTO
    recommend_result.py          # 출력 DTO
  ports/
    input/
      recommend_use_case.py      # RecommendUseCase(ABC) — recommend() 하나만
    output/
      preference_repository_port.py   # 선호도 읽기/누적 저장
      recommendation_chain_port.py    # LangChain 체인 실행 포트
  use_cases/
    recommend_interactor.py
dependencies/
  recommend_director.py          # 체인·Repository·Interactor 조립
adapter/
  outbound/
    orm/preference_model.py
    pg/preference_pg_repository.py
    langchain/
      recommendation_chain.py    # ChatPromptTemplate | LLM 조립 (여기서만 LangChain 심볼 사용)
  inbound/
    api/v1/recommend_router.py
    schemas/recommend_schemas.py
    mappers/recommend_mapper.py
```

**ISP 준수:** `RecommendUseCase`에는 `recommend()` 한 메서드만 둔다. 선호도 누적 저장은 별도 `PreferenceUseCase.record_feedback()`로 분리한다 (읽기/쓰기 혼합 금지).

---

## 3. 체인 설계

1. **입력 결합** — `PreferenceProfile`(누적 선호, DB) + `RecommendationCriteria`(이번 요청, 실시간)를 하나의 프롬프트 컨텍스트로 병합한다.
2. **프롬프트 분리** — `adapter/outbound/langchain/prompts/recommend_prompt.py`에 시스템/유저 프롬프트를 정의한다. Interactor에는 문자열을 두지 않는다.
3. **모델 스왑 가능하게** — `recommend_director.py`에서 LLM 인스턴스를 주입한다. 기본은 Gemini, 로컬 폴백은 EXAONE(vLLM) — [[local_llm_exaone]] 참고.
4. **실시간 갱신** — 대화 세션 내 조건 변경은 새 `RecommendationCriteria`로만 반영하고, `PreferenceProfile`은 세션 종료 후 별도 배치/이벤트로 누적 갱신한다 (매 턴마다 쓰기 금지 — 성능 저하 방지, [[003-langchain-harness]] §2 참고).

```python
# adapter/outbound/langchain/recommendation_chain.py
class RecommendationChain(RecommendationChainPort):
    def __init__(self, llm: BaseChatModel):
        self._llm = llm
        self._prompt = RECOMMEND_PROMPT  # 별도 파일에서 import

    async def run(self, profile: PreferenceProfile, criteria: RecommendationCriteria) -> str:
        chain = self._prompt | self._llm
        result = await chain.ainvoke({"profile": profile, "criteria": criteria})
        return result.content
```

---

## 4. 체크리스트

- [ ] `RecommendUseCase`가 추천 조회 외 다른 책임(저장 등)을 갖지 않는가? (ISP)
- [ ] 프롬프트가 `recommend_prompt.py`로 분리되어 있는가?
- [ ] 선호도 누적 쓰기가 매 요청마다 발생하지 않는가? (성능)
- [ ] LLM 인스턴스가 Director에서 주입되어 모델 교체가 가능한가?
- [ ] `python main.py` 기동 후 실제 추천 응답을 확인했는가?

---

*이 문서는 LangChain 고객 사례(NCL)를 근거로 한 구현 전략이며, 실제 NCL 시스템 내부 구조를 재현한 것이 아니다.*

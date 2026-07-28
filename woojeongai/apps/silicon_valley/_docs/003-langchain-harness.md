# 003 — LangChain 하네스 (silicon_valley)

> 클로드가 이 저장소에서 LangChain 관련 코드를 작성·수정할 때 반드시 따르는 행동 규칙.
> 전역 원칙은 [[../../../CLAUDE|모노레포 루트 CLAUDE.md]], 백엔드 규칙은 [[../../CLAUDE|woojeongai/CLAUDE.md]] 를 따른다.

---

## 0. LangChain을 왜 쓰는가 (판단 기준)

LangChain은 "모든 LLM 작업의 기본값"이 아니다. 아래 강점이 실제로 필요한 경우에만 도입한다.

| 강점 | silicon_valley에서의 활용 지점 |
|------|-------------------------------|
| 다양한 데이터 소스 통합 | Neo4j GraphRAG, PDF 파이프라인, 외부 API 호출을 하나의 체인/그래프로 엮을 때 |
| 유연한 프롬프팅·컨텍스트 관리 | 멀티턴 캐스팅 대화, 페르소나별 시스템 프롬프트 관리 |
| 파인튜닝·모델 교체 용이성 | Gemini ↔ 로컬 EXAONE(vLLM) 등 모델 스왑이 필요할 때 |
| 데이터 반응형 앱 | LangGraph 기반 실시간 상태 갱신 워크플로우 |

→ 위 표에 해당하지 않는 **단순 1회성 LLM 호출**은 LangChain 없이 SDK 직접 호출로 처리한다. (불필요한 추상화 금지 — 루트 CLAUDE.md 원칙과 동일)

---

## 1. 반드시 지킬 것 (Do)

1. **체인/그래프 조립은 `dependencies/*_director.py`에서만** — 백엔드 클린 아키텍처 원칙(woojeongai/CLAUDE.md §3.3)을 그대로 따른다. 라우터·Interactor에서 `ChatPromptTemplate`, `Chain`, `Graph`를 직접 생성하지 않는다.
2. **프롬프트는 별도 파일로 분리** (`app/prompts/*.py` 등) — 라우터·Interactor 코드에 긴 프롬프트 문자열을 인라인으로 넣지 않는다.
3. **외부 데이터 소스 연동(Neo4j, API, 파일 등)은 outbound adapter로 캡슐화** — `RunnableLambda`나 커스텀 Retriever 내부에서 직접 DB 커넥션을 열지 않고, 기존 Repository/Port 패턴을 재사용한다.
4. **모델 교체 가능성을 항상 열어둔다** — LLM 인스턴스는 하드코딩하지 않고 Director/DI에서 주입한다. (Gemini ↔ EXAONE-vLLM 스왑 사례 참고: [[local_llm_exaone]])
5. **컨텍스트/메모리는 명시적으로 관리** — 대화 히스토리를 암묵적 전역 상태로 두지 않고, DTO/세션 단위로 전달한다.
6. **체인 실행 후 반드시 로컬 실행으로 검증** — `python main.py` 기동 후 실제 요청으로 체인 출력 확인. mypy/ruff 통과만으로 완료 선언 금지.

---

## 2. 하지 말 것 (Don't) — LangChain 단점에서 도출한 안티패턴

| 단점 | 대응 규칙 |
|------|-----------|
| 성능 저하 (복잡한 체인에서 연산 부담 증가) | 불필요하게 체인을 길게 쌓지 않는다. 단순 프롬프트 호출에 `Chain`/`Graph`를 씌우지 않는다. 성능이 중요한 구간은 직접 호출로 단순화한다. |
| 초심자 러닝커브 | 이 저장소의 기존 체인 구조를 임의로 새 패턴으로 바꾸지 않는다. 같은 목적의 체인이 이미 있으면 그 패턴을 재사용한다. |
| 일부 유즈케이스 부적합 | 고도로 특화된 성능/비용 요구가 있는 구간(예: 대량 배치 처리)은 LangChain 대신 직접 구현이 적합한지 먼저 검토하고, 애매하면 사용자에게 확인한다. |

**추가 금지 사항**

```python
# ❌ 라우터에서 체인 직접 조립
@router.post("/cast")
async def cast(req: Request):
    chain = ChatPromptTemplate.from_template(...) | ChatOpenAI()
    return chain.invoke(...)

# ✅ Director에서 조립, 라우터는 Use Case만 호출
@router.post("/cast")
async def cast(
    use_case: CastingUseCase = Depends(get_casting_use_case),
) -> CastingResponse:
    result = await use_case.cast(...)
    return casting_dto_to_response(result)
```

---

## 3. 작업 후 체크리스트

- [ ] 체인/그래프 조립이 `dependencies/*_director.py`에만 있는가?
- [ ] 프롬프트가 코드와 분리된 파일에 있는가?
- [ ] 모델(LLM) 인스턴스가 하드코딩이 아닌 주입 방식인가?
- [ ] 불필요하게 복잡한 체인 대신 가장 단순한 구조를 선택했는가?
- [ ] 실제로 `python main.py` 기동 후 응답을 확인했는가?
- [ ] `ruff check . --fix && ruff format . && mypy . --ignore-missing-imports` 통과했는가? (woojeongai/CLAUDE.md 하네스)

---

*이 문서는 LangChain 기능/장단점 요약을 근거로 클로드의 행동 규칙만 정의한다. LangChain 자체 API 문서가 아니다.*

# 004 — LangGraph 하네스 (silicon_valley)

> 클로드가 이 저장소에서 LangGraph 관련 코드를 작성·수정할 때 반드시 따르는 행동 규칙.
> 전역 원칙은 [[../../../CLAUDE|모노레포 루트 CLAUDE.md]], 백엔드 규칙은 [[../../CLAUDE|woojeongai/CLAUDE.md]],
> LangChain 공통 규칙은 [[003-langchain-harness]], 그래프 DB 규칙은 [[002-neo4j-harness]] 를 함께 따른다.
> 이 문서는 그중 **"시멘틱 라우터가 reasoning 의도로 분류한 질문"** 을 처리하는 경로만 다룬다.

---

## 0. LangGraph를 왜 쓰는가 (판단 기준)

[[003-langchain-harness]] §0의 "체인이 필요할 때만 도입" 원칙을 그대로 계승한다. LangGraph는 "모든 대화의 기본값"이 아니라, **선형 체인(`prompt | llm`)으로 표현이 안 되는 워크플로우**에만 도입한다.

| 선형 체인의 한계 | LangGraph가 해결하는 방식 | silicon_valley 적용 지점 |
|------------------|---------------------------|---------------------------|
| A→B→C 단방향, 되돌아가기 불가 | 조건부 엣지(conditional edge)로 특정 노드로 회귀 | 근거 부족 시 그래프 재조회 → 재답변 루프 |
| 중간 판단·재시도 횟수를 별도로 들고 다닐 수 없음 | `State`(TypedDict/BaseModel) 하나에 누적·공유 | 검색 문서, 재시도 횟수, 검증 결과를 한 곳에서 관리 |
| 오류 시 스스로 고치는 경로가 없음 | 자기 수정(Self-correction) 노드 + 조건부 엣지 | 근거 없는 답변(환각) 감지 시 재검색 후 재생성 |
| 역할이 다른 여러 LLM 호출을 한 체인에 억지로 구겨넣음 | 노드별 역할 분리(리서치/검증/작성) | 그래프 컨텍스트 조회 노드 / 답변 생성 노드 / 근거 검증 노드 |

**현재 저장소의 실제 참조 패턴** — silicon_valley에는 아직 시멘틱 라우터가 없다. 참조할 정본은 `star_craft` 앱이다.

- `star_craft/app/use_cases/semantic_router_interactor.py` — `SemanticRouterInteractor.route()`가 임베딩 코사인 유사도로 `SemanticIntent.GRAPH / GENERAL / CODING` 3종을 분류하고, 각 의도를 `GraphQaUseCase` / Gemini 직접 호출 / `LangchainChatUseCase`로 단락(short-circuit) 위임한다.
- `star_craft/domain/services/semantic_intent_classifier.py` — 순수 도메인 함수 `classify_intent()`. 의도별 예시 문장 임베딩과의 최대 코사인 유사도를 비교하고, 오분류 비용이 비대칭적이라는 이유로 애매하면 `GENERAL` 쪽으로 기울이는 confidence margin(`0.03`)을 둔다.
- silicon_valley에 시멘틱 라우터를 도입할 때는 이 패턴에 **`SemanticIntent.REASONING`을 한 항목 추가**하고, `classify_intent()`에 `reasoning_score`를 같은 방식(마진 비교)으로 끼워 넣는다 — 새 클래스 위계를 만들지 않는다(OPEN/CLOSED, woojeongai/CLAUDE.md §4 O 원칙).
- 하드게이트 방식이 더 맞는 도메인(정형화된 트리거 단어가 있는 경우)이라면 `titanic/app/use_cases/crew_andrews_architect_interactor.py`(Andrews Architect)의 Stage 1/2 하드게이트 → Stage 3 ML 폴백 구조를 참고한다. 어느 쪽이든 **"reasoning"은 하드게이트로 즉시 확정하지 않는다** — 다단계 추론이 필요한지는 문맥 의존적이라 오분류 비용이 낮은 임베딩/ML 폴백 쪽에 맡긴다.

> "reasoning" 의도의 판단 기준: 페르소나 간 관계·조직 정치·인과관계에 걸친 **다단계(Multi-hop)** 질문. 예) "리처드가 이번 결정을 내리면 길포일과 디네시 사이 역학은 어떻게 바뀔까?" 단일 사실 조회(예: "리처드 직급이 뭐야")는 GRAPH 또는 GENERAL로 남긴다 — 불필요하게 LangGraph로 보내지 않는다.

---

## 1. 아키텍처 위치

```
domain/
  services/
    semantic_intent_classifier.py   # (신규, star_craft 패턴 재사용) REASONING 포함 확장
  constants/
    semantic_intent_examples.py     # REASONING 예시 문장 추가
app/
  dtos/
    reasoning_state_dto.py          # LangGraph State와 1:1 대응하는 경계용 DTO (선택)
  ports/
    input/
      reasoning_graph_use_case.py   # ReasoningGraphUseCase(ABC) — run() 하나만 (ISP)
    output/
      graph_context_port.py         # Neo4j GraphRAG 조회 포트 (002-neo4j-harness 정의 재사용)
  use_cases/
    reasoning_graph_interactor.py   # 컴파일된 LangGraph를 호출만 함 — 그래프 구조 모름
dependencies/
  reasoning_graph_director.py       # StateGraph 조립 + compile() — 여기서만 langgraph 심볼 사용
adapter/
  outbound/
    langgraph/
      reasoning_state.py            # State TypedDict/BaseModel 정의
      nodes/
        retrieve_graph_context.py   # Neo4j GraphRAG 조회 노드
        generate_answer.py          # LangChain(Gemini) 답변 생성 노드
        verify_grounding.py         # 근거 충분성 검증 노드 (self-correction)
      reasoning_graph_builder.py    # add_node/add_conditional_edges 조립, compile()은 director에서 1회 호출
```

**ISP 준수:** `ReasoningGraphUseCase`에는 `run(question: str) -> ReasoningResult` 한 메서드만 둔다. 그래프 구조·노드 순서는 Use Case가 알 필요 없다 — director가 조립한 컴파일 그래프를 주입받아 `ainvoke()`만 호출한다.

> **네이밍 갭 주의:** silicon_valley의 `dependencies/`에는 현재 `*_provider.py`(단순 Depends 팩토리, 예: `gemini_provider.py`, `piper_hendricks__ceo_provider.py`)만 존재하고 `*_director.py`는 아직 없다. 이 문서는 woojeongai/CLAUDE.md §3.3·[[003-langchain-harness]]가 명시한 "체인/그래프 조립은 `*_director.py`에서만" 원칙을 그대로 따르므로, LangGraph 조립 파일은 기존 `*_provider.py`와 구분해 `*_director.py`로 새로 만든다. 단순 인스턴스 주입(`get_gemini_client`류)까지 director로 바꾸라는 뜻은 아니다 — 그래프/체인 조립이 있는 경우에만 이 네이밍을 쓴다.
>
> **참고할 기존 코드:** silicon_valley에 아직 LangGraph/LangChain 코드는 없지만, `app/use_cases/piper_hendricks__ceo_interactor.py`의 `HendricksCeoInteractor.chat()`이 가장 가까운 선례다 — 메시지 임베딩 → `SongRagPort.search_similar_songs`(pgvector 조회) → 컨텍스트 포맷팅 → 페르소나 프롬프트 결합 → Gemini 호출의 수작업 RAG 흐름이다. §4의 `retrieve_graph_context`/`generate_answer` 노드는 이 흐름을 LangGraph 노드로 재구성한 것이라고 보면 된다(단, 소스는 pgvector 대신 Neo4j GraphRAG).

---

## 2. 반드시 지킬 것 (Do)

1. **그래프 조립은 `dependencies/reasoning_graph_director.py`에서만** — `StateGraph`, `add_node`, `add_conditional_edges`, `compile()`을 라우터·Interactor에서 직접 호출하지 않는다. (woojeongai/CLAUDE.md §3.3 Director 패턴과 동일)
2. **State는 명시적 타입으로 정의** — `TypedDict`(langgraph 관례) 또는 `pydantic.BaseModel`로 `adapter/outbound/langgraph/reasoning_state.py`에 선언한다. 딕셔너리를 인라인으로 주고받지 않는다.
3. **노드 함수는 순수 함수처럼 작성** — Gemini 호출, Neo4j 조회 같은 외부 I/O는 노드 내부에서 직접 하지 않고 기존 Port(`GraphQueryPort` 등, [[002-neo4j-harness]] 참고)를 주입받아 위임한다. `star_craft/adapter/outbound/neo4j/neo4j_graph_query_repository.py`처럼 드라이버는 조회 시점에만 열고 생성자에서 연결하지 않는 패턴을 재사용한다.
4. **조건부 엣지는 반드시 종료 조건을 가진다** — `State`에 `retry_count` 필드를 두고, `verify_grounding` 노드가 "근거 부족"으로 판단해도 `retry_count >= 2`면 무조건 `END`로 보낸다. 무한 루프 금지가 최우선이다.
5. **컴파일된 그래프는 프로세스당 1회 생성 후 재사용** — `reasoning_graph_director.py`에서 모듈 스코프 캐시 또는 FastAPI lifespan에서 한 번만 `compile()`하고, 요청마다 `StateGraph`를 재구성하지 않는다. (`star_craft/semantic_router_interactor.py`의 `_example_vectors_cache` 캐싱 패턴과 동일한 이유 — 프로세스당 1회 비용으로 상각)
6. **REASONING 의도일 때만 이 그래프를 호출한다** — 시멘틱 라우터가 GRAPH/GENERAL/CODING(또는 titanic 방식 count/personal 등)으로 분류한 경우는 기존 단일 체인/직접 LLM 호출을 그대로 쓴다. 모든 질문을 LangGraph로 흘려보내지 않는다 (§0 판단 기준, 루트 CLAUDE.md 불필요한 추상화 금지 원칙).
7. **GraphRAG 조회와 생성을 분리** — Neo4j에서 관계 컨텍스트를 가져오는 노드와 그 컨텍스트로 답변을 생성하는 노드를 하나로 합치지 않는다. 검증 노드가 재조회를 요청할 수 있어야 하기 때문이다.
8. **모델 교체 가능성 유지** — 답변 생성 노드의 LLM 인스턴스는 director에서 주입한다(Gemini ↔ 로컬 EXAONE 스왑, [[003-langchain-harness]] §1.4 참고).
9. **실행 후 반드시 로컬 검증** — `python main.py` 기동 후 실제 reasoning 질문으로 조건 분기·루프 종료를 눈으로 확인한다. mypy/ruff 통과만으로 완료 선언 금지.

---

## 3. 하지 말 것 (Don't)

| 상황 | 대응 규칙 |
|------|-----------|
| 단순 조회형 질문(단일 사실, 단순 검색)에도 그래프를 태우고 싶어짐 | 하지 않는다. 선형 체인/직접 호출로 충분하면 LangGraph를 씌우지 않는다 — 오버엔지니어링. |
| 라우터·Interactor에서 그래프 구조를 알아야 할 것 같은 유혹 | `ReasoningGraphUseCase.run()` 뒤에 완전히 숨긴다. 호출부는 컴파일된 그래프의 존재만 안다. |
| 노드 안에서 `neo4j.AsyncGraphDatabase.driver(...)`를 직접 생성 | Port/Repository를 주입받는다 (§2.3). |
| `add_conditional_edges`에 종료 조건 없이 루프 구성 | 항상 `retry_count`/`max_iteration` 기반 탈출 경로를 함께 정의한다. |
| 요청마다 `workflow.compile()` 재호출 | 프로세스 시작 시 1회만 컴파일한다 (§2.5). |

```python
# ❌ 라우터에서 그래프 직접 조립 + 매 요청 컴파일
@router.post("/ask")
async def ask(req: Request):
    workflow = StateGraph(ReasoningState)
    workflow.add_node("retrieve", retrieve_graph_context)
    workflow.add_node("answer", generate_answer)
    app = workflow.compile()
    return await app.ainvoke({"question": req.message})

# ✅ Director에서 1회 컴파일, Use Case는 실행만 위임
@router.post("/ask")
async def ask(
    reasoning: ReasoningGraphUseCase = Depends(get_reasoning_graph_use_case),
) -> ReasoningResponse:
    result = await reasoning.run(req.message)
    return reasoning_result_to_response(result)
```

---

## 4. 그래프 설계 — reasoning 의도 처리 예시

**State (`adapter/outbound/langgraph/reasoning_state.py`)**

```python
from typing import TypedDict


class ReasoningState(TypedDict):
    question: str
    graph_context: list[dict]   # Neo4j GraphRAG 조회 결과
    draft_answer: str
    is_grounded: bool           # verify_grounding 노드의 판단
    retry_count: int
```

**노드 (`adapter/outbound/langgraph/nodes/`)** — 각 노드는 기존 Port만 의존한다.

```python
# retrieve_graph_context.py — Neo4j GraphRAG 조회 (002-neo4j-harness §Text-to-Cypher/하이브리드 검색 참고)
async def retrieve_graph_context(state: ReasoningState, *, graph_query: GraphQueryPort) -> dict:
    records = await graph_query.find_related_context(state["question"])
    return {"graph_context": records}

# generate_answer.py — LangChain(Gemini) 답변 생성, 프롬프트는 별도 파일 분리
async def generate_answer(state: ReasoningState, *, llm: BaseChatModel) -> dict:
    chain = REASONING_ANSWER_PROMPT | llm
    result = await chain.ainvoke({
        "question": state["question"],
        "context": state["graph_context"],
    })
    return {"draft_answer": str(result.content)}

# verify_grounding.py — 근거 충분성 검증 (self-correction 트리거)
async def verify_grounding(state: ReasoningState, *, llm: BaseChatModel) -> dict:
    verdict = await _check_grounded(state["draft_answer"], state["graph_context"], llm)
    return {"is_grounded": verdict, "retry_count": state["retry_count"] + 1}
```

**조립 (`dependencies/reasoning_graph_director.py`)** — 유일하게 `langgraph` 심볼을 쓰는 위치.

```python
from functools import lru_cache

from langgraph.graph import END, StateGraph

def _should_retry(state: ReasoningState) -> str:
    if state["is_grounded"] or state["retry_count"] >= 2:   # 종료 조건 필수
        return "end"
    return "retry"

@lru_cache
def build_reasoning_graph(graph_query: GraphQueryPort, llm: BaseChatModel):
    workflow = StateGraph(ReasoningState)
    workflow.add_node("retrieve", partial(retrieve_graph_context, graph_query=graph_query))
    workflow.add_node("answer", partial(generate_answer, llm=llm))
    workflow.add_node("verify", partial(verify_grounding, llm=llm))

    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "answer")
    workflow.add_edge("answer", "verify")
    workflow.add_conditional_edges("verify", _should_retry, {"retry": "retrieve", "end": END})

    return workflow.compile()  # 프로세스당 1회
```

> `lru_cache`(또는 FastAPI lifespan 싱글턴)로 감싸는 이유는 §2.5 — 컴파일 비용을 요청마다 지불하지 않기 위함이다.

---

## 5. 시멘틱 라우터 통합 지점

silicon_valley용 라우터(`SemanticRouterInteractor` 상당)가 만들어지면, 분기는 `star_craft` 패턴을 그대로 따르되 한 항목만 추가한다.

```python
# domain/services/semantic_intent_classifier.py (star_craft 패턴 확장)
class SemanticIntent(str, Enum):
    GRAPH = "graph"
    GENERAL = "general"
    CODING = "coding"
    REASONING = "reasoning"   # 다단계 추론 — LangGraph 위임


# app/use_cases/semantic_router_interactor.py (확장)
async def route(self, message: str) -> str:
    intent = classify_intent(query_vector, examples[...])
    if intent is SemanticIntent.REASONING:
        result = await self.reasoning_graph.run(message)   # ReasoningGraphUseCase
        return result.draft_answer
    if intent is SemanticIntent.GRAPH:
        return await self.graph_qa.answer(message)
    ...
```

`classify_intent()`에는 `reasoning_score`를 다른 의도와 동일한 마진 비교 방식(`star_craft/domain/services/semantic_intent_classifier.py`의 `_GRAPH_CONFIDENCE_MARGIN` 패턴)으로 추가한다 — 새 if/elif 사슬을 만들지 않는다.

---

## 6. 사전 준비 — 의존성

- `langgraph` 패키지가 `requirements.txt`에 아직 없다 — 도입 전 추가 필요.
- `langchain-core`, `langchain-google-genai`, `neo4j==5.28.1`, `neo4j-graphrag==1.18.0`은 이미 설치되어 있다 — Text-to-Cypher/하이브리드 검색 노드는 `neo4j-graphrag`를 우선 활용하고, 직접 Cypher가 필요하면 `star_craft/adapter/outbound/neo4j/neo4j_graph_query_repository.py` 패턴(조회 시점에만 드라이버 오픈)을 재사용한다.

---

## 7. 작업 후 체크리스트

- [ ] 그래프 조립(`StateGraph`/`add_node`/`compile`)이 `dependencies/reasoning_graph_director.py`에만 있는가?
- [ ] `State`가 명시적 TypedDict/BaseModel로 정의되어 있는가?
- [ ] 모든 노드가 순수 함수 형태이고, 외부 I/O는 주입된 Port를 통해서만 발생하는가?
- [ ] 모든 조건부 엣지에 `retry_count`/`max_iteration` 기반 종료 조건이 있는가?
- [ ] 컴파일된 그래프가 요청마다 재생성되지 않고 캐싱되는가?
- [ ] REASONING 의도가 아닌 질문까지 LangGraph를 거치지 않는가?
- [ ] `requirements.txt`에 `langgraph`가 추가되었는가?
- [ ] `python main.py` 기동 후 실제 reasoning 질문으로 루프 종료·최종 답변을 확인했는가?
- [ ] `ruff check . --fix && ruff format . && mypy . --ignore-missing-imports` 통과했는가? (woojeongai/CLAUDE.md 하네스)

---

*이 문서는 LangChain→LangGraph 확장 근거와 GraphRAG(Neo4j) 활용법 요약을 근거로 클로드의 행동 규칙만 정의한다. LangGraph/Neo4j 자체 API 문서가 아니며, 그래프 데이터 적재(Ingestion) 파이프라인 자체는 [[002-neo4j-harness]]의 범위다.*

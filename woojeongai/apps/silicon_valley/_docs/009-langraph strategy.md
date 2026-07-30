# 009 — LangGraph 전략: GraphCypherQAChain 기반 동적 Text-to-Cypher

> 참고 코드: `Neo4jGraph` + `GraphCypherQAChain`(langchain_community)으로 자연어 질문을
> 자동으로 Cypher 쿼리로 변환·실행하고, LangGraph로 조회→검증→답변 루프를 구성한 예시.
> 이 문서는 이 코드에서 얻을 수 있는 전략만 정리한다 — 그대로 이식하는 문서가 아니다.
> [[004-langgraph-harness]](행동 규칙), [[002-neo4j-harness]](그래프 DB 규칙, 현재 미작성),
> [[003-langchain-harness]](LangChain 공통 규칙)를 함께 따른다.

---

## 1. 참고 코드가 제안하는 것 vs 우리 저장소의 기존 방식

이 코드의 핵심은 **"Cypher 쿼리 자체를 LLM이 그때그때 생성해서 실행한다"**(`GraphCypherQAChain`)는 점이다. 이는 이미 `star_craft`에 구현된 방식과 근본적으로 다르다.

| 구분 | 참고 코드 (`GraphCypherQAChain`) | 현재 `star_craft` 구현 (`neo4j_graph_query_repository.py`) |
|------|-----------------------------------|--------------------------------------------------------------|
| 쿼리 생성 방식 | LLM이 질문마다 **새 Cypher를 즉석 생성** | 개발자가 미리 작성한 **고정된 1개 쿼리**만 실행 |
| 표현력 | 임의의 관계·패턴 질문에 대응 가능 (유연) | 정해진 질문(최근 분류 목록)만 답변 가능 (제한적) |
| 보안 위험 | LLM이 생성한 쿼리를 그대로 실행 — **오염·오조회·쓰기 쿼리 위험** | 쿼리가 코드에 고정돼 있어 위험 없음 |
| 적합한 상황 | "리처드와 길포일 사이 관계는?" 같은 **예측 불가능한 다단계 질문** | "최근 분류 데이터 보여줘" 같은 **정형화된 질문** |

**결론: 이 둘은 대체 관계가 아니라 보완 관계다.** 시멘틱 라우터의 `GRAPH` 의도(정형 질문)는 기존 `GraphQueryPort` 고정 쿼리 방식을 그대로 쓰고, [[004-langgraph-harness]]가 정의한 `REASONING` 의도(다단계·예측 불가능 질문)에서만 `GraphCypherQAChain` 방식을 검토한다.

---

## 2. 반드시 짚어야 할 위험 — `allow_dangerous_requests=True`

참고 코드에 그대로 있는 이 플래그는 **LLM이 생성한 임의의 Cypher를 검증 없이 실행**하도록 허용한다. 이건 SQL 인젝션과 동일한 급의 위험이다 — LLM이 실수로(또는 프롬프트 인젝션으로) `DELETE`/`DETACH DELETE`/`SET` 같은 쓰기 쿼리를 생성하면 그래프 데이터가 훼손될 수 있다.

이 전략을 실제로 도입한다면 **최소 다음 중 하나는 반드시 갖춘다** (택1이 아니라 방어 계층으로 여러 개 병행 권장):

1. **읽기 전용 DB 계정 분리** — `GraphCypherQAChain`이 쓰는 Neo4j 드라이버는 `MATCH`/`RETURN`만 가능한 읽기 전용 role의 계정을 쓴다. 쓰기 권한이 있는 계정(`neo4j_graph_query_repository.py`가 쓰는 것과 동일 계정)을 그대로 재사용하지 않는다.
2. **생성된 쿼리 사전 검사** — 실행 전에 쿼리 문자열에 `CREATE|DELETE|SET|MERGE|REMOVE|DROP` 등의 키워드가 있으면 차단하는 가드를 `GraphQueryPort` 구현체 안에 둔다.
3. **`allow_dangerous_requests`를 그대로 켜지 않는다** — 대신 `GraphCypherQAChain`의 쿼리 생성 단계와 실행 단계를 분리해, 생성된 Cypher를 노드 간 State(`draft_cypher`)에 담아 검증 노드를 한 번 거치게 한다 (LangGraph의 노드 분리 이점을 그대로 활용).

---

## 3. 우리 아키텍처에 얹는 법 (기존 패턴 재사용)

`GraphCypherQAChain`은 결국 "질문 → Cypher 생성 → 실행 → 자연어 요약"까지 한 번에 처리하는 하나의 체인이다. 이걸 LangGraph 노드 하나로 뭉치지 않고, [[004-langgraph-harness]] §2.7(조회와 생성 분리 원칙)에 맞춰 쪼갠다.

```
adapter/outbound/langgraph/nodes/
  generate_cypher.py       # 질문 → Cypher 문자열 생성만 (LLM 호출, 실행 안 함)
  validate_cypher.py       # 위험 키워드 검사 — §2의 가드 (순수 함수, LLM/DB 호출 없음)
  execute_cypher.py        # 검증 통과한 쿼리만 GraphQueryPort로 실행
  generate_answer.py       # 004-langgraph-harness §4와 동일 — 조회 결과로 답변 생성
```

- `generate_cypher`/`execute_cypher`는 각각 [[003-langchain-harness]]의 "체인 조립은 outbound에서만", [[004-langgraph-harness]] §2.3(노드는 Port만 의존)을 따른다 — `Neo4jGraph`·`GraphCypherQAChain` 객체는 `adapter/outbound/langgraph/` 밖으로 나가지 않는다.
- `validate_cypher`는 외부 I/O가 없는 순수 함수라 [[004-langgraph-harness]] §2.3의 "노드는 순수 함수처럼" 원칙에 가장 잘 들어맞는 예시다.
- `State`(`ReasoningState`, 004 §4 정의)에 `draft_cypher: str` 필드 하나만 추가하면 된다 — 새 State 타입을 만들지 않는다.

---

## 4. 모델·인프라 — 참고 코드 그대로 쓰면 안 되는 부분

참고 코드는 `ChatOpenAI(model="gpt-4o-mini")`를 쓰지만, 이 저장소에는 OpenAI 연동이 없다 (Gemini·로컬 EXAONE만 구성돼 있음, [[003-langchain-harness]] §1.4). 이 전략을 실제로 옮길 때:

- OpenAI API 키를 새로 발급받지 않는다. 기존 `langchain-google-genai`(`ChatGoogleGenerativeAI`)로 교체한다 — `star_craft/adapter/outbound/repositories/langchain_chat_repository.py`가 이미 이 패턴의 정본이다.
- Cypher 생성용 LLM과 최종 답변 생성용 LLM을 반드시 같은 모델로 묶어둘 필요는 없다 — Cypher 생성은 더 저렴한 모델로, 최종 답변은 품질이 더 필요하면 다른 등급으로 분리하는 것도 고려 가능하다 (지금 당장 결정할 사항은 아니고, 도입 시점에 재논의).
- `NEO4J_URI`/`NEO4J_USERNAME`/`NEO4J_PASSWORD` 환경 변수명이 참고 코드와 우리 `.env`(`NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD`)가 다르다 — 그대로 복붙하면 `NEO4J_USERNAME`이 안 읽힌다. 기존 변수명(`NEO4J_USER`)에 맞춘다.

---

## 5. 참고 코드에서 그대로 가져오면 안 되는 것들 (체크리스트性 요약)

| 참고 코드 | 문제 | 대응 |
|-----------|------|------|
| `print()`으로 노드 진행 로깅 | woojeongai 로깅 규칙(레이어당 1줄, `logging_setup.py` 등록) 위반 | `logger.info()` + 등록된 로거 사용 |
| `if __name__ == "__main__":` 하단 테스트 실행 | 프로덕션 코드에 스크립트 진입점 혼재 | 별도 `tests/`로 분리, [[004-langgraph-harness]] §2.9(로컬 검증)는 `python main.py` 기동 후 실제 엔드포인트로 |
| `evaluate_context_node`가 문자열 매칭(`"찾지 못했습니다" not in context`)으로 충분성 판단 | 휴리스틱이 너무 약함 — 근거 없이도 통과 가능 | [[004-langgraph-harness]] §4의 `verify_grounding`(LLM 기반 근거 검증)으로 대체 |
| `GraphCypherQAChain.from_llm(..., allow_dangerous_requests=True)` | §2의 보안 위험 | §2·§3의 검증 노드 분리 구조로 대체 |
| 매 실행마다 `Neo4jGraph`/`ChatOpenAI` 전역 인스턴스 생성 | director/provider 조립 원칙 위반 (woojeongai/CLAUDE.md §3.3) | `dependencies/reasoning_graph_director.py`에서 주입 |

---

## 6. 작업 후 체크리스트

- [ ] `GraphCypherQAChain` 방식은 `REASONING` 의도 전용이고, `GRAPH` 의도(정형 질문)는 기존 고정 쿼리를 그대로 쓰는가?
- [ ] Cypher 생성(`generate_cypher`)과 실행(`execute_cypher`)이 분리되어 있고, 그 사이에 `validate_cypher` 검증 노드가 있는가?
- [ ] 쓰기 쿼리(`CREATE`/`DELETE`/`SET`/`MERGE`/`REMOVE`/`DROP`) 생성 시 실행을 차단하는 가드가 있는가? 또는 읽기 전용 DB 계정을 쓰는가?
- [ ] `allow_dangerous_requests=True`를 검증 없이 그대로 켜지 않았는가?
- [ ] LLM이 OpenAI가 아니라 기존 Gemini/EXAONE 인프라로 교체되었는가?
- [ ] 환경 변수명이 `NEO4J_USER`(우리 규약)와 일치하는가? (`NEO4J_USERNAME` 아님)
- [ ] `print()` 대신 등록된 로거를 쓰는가?
- [ ] 근거 충분성 판단이 문자열 매칭이 아니라 LLM 기반 검증(`verify_grounding`)인가?
- [ ] [[004-langgraph-harness]] §2(director 조립, State 타입, 노드 순수성, 종료 조건, 컴파일 캐싱)를 모두 만족하는가?

---

*이 문서는 사용자가 제시한 참고 코드(Neo4jGraph+GraphCypherQAChain+LangGraph)에서 우리 저장소에 적용 가능한 전략만 추출한 것이며, 코드 구현은 포함하지 않는다. 실제 구현 시 [[004-langgraph-harness]]가 정의한 디렉터리 구조·Do/Don't를 그대로 따른다.*

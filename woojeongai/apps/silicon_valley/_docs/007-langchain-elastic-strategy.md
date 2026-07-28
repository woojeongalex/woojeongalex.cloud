# 007 — LangChain 전략: Elastic 사례 (운용 효율성 향상)

> 참고 사례: Elastic은 LangChain의 데이터 통합·실시간 처리 기능을 활용해 보안 분석가를 지원하는
> AI 어시스턴트를 구축했다 — 보안 경고 요약, 워크플로우 제안, 쿼리 생성·변환.
> 본 문서는 이 사례를 silicon_valley/woojeongai 운영 도메인에 적용하는 구현 전략을 정의한다.
> 공통 행동 규칙은 [[003-langchain-harness]] 를 우선 따른다.

---

## 1. 사례 → woojeongai 적용 대상

| Elastic 사례 | woojeongai 적용 대상 |
|--------------|------------------------|
| 보안 경고 요약 | 도메인 로그(`logging_setup.py`) / 에러 스택 요약 |
| 워크플로우 제안 | 장애·이상 패턴에 대한 대응 절차 제안 (Alembic 롤백, 재시작 등) |
| 쿼리 생성·변환 | 자연어 → Cypher(Neo4j) / SQL(pgvector) 쿼리 자동 생성 |
| 대량 실시간 데이터 처리 | Neo4j GraphRAG 파이프라인, 로그 스트림 |

핵심은 **"운영자가 직접 로그·쿼리를 뒤지지 않아도, AI가 요약·제안·쿼리 초안을 대신 만들어주는 보조 어시스턴트"**다. 이 어시스턴트는 자동 실행 권한을 갖지 않고, 항상 사람이 최종 승인 후 실행한다.

---

## 2. 아키텍처

```
domain/
  entities/
    ops_alert.py                 # 요약 대상 로그/경고 이벤트
  value_objects/
    query_draft.py               # 생성된 쿼리 초안 (frozen, 미실행 상태)
app/
  dtos/
    ops_summarize_command.py
    ops_summarize_result.py
    query_generate_command.py
    query_generate_result.py
  ports/
    input/
      ops_assistant_use_case.py  # summarize_alerts(), draft_query() — 두 메서드로 분리 (ISP)
    output/
      log_source_port.py         # 로그 소스 읽기 (DB/파일/스트림 추상화)
      query_chain_port.py        # LangChain 쿼리 생성 체인
  use_cases/
    ops_assistant_interactor.py
dependencies/
  ops_assistant_director.py
adapter/
  outbound/
    langchain/
      alert_summary_chain.py
      query_generation_chain.py  # Cypher/SQL 변환 프롬프트+파서
    log/log_source_reader.py     # 기존 로거 출력 소스 어댑터
  inbound/
    api/v1/ops_assistant_router.py
```

**ISP 준수:** `summarize_alerts()`(읽기 전용 요약)와 `draft_query()`(쿼리 초안 생성)를 하나의 Fat 인터페이스로 묶지 않는다. 실제 쿼리 **실행**은 이 Use Case에 포함하지 않는다 — 실행은 별도의 승인 절차를 거치는 다른 경로로 둔다.

---

## 3. 체인 설계

1. **로그 요약 체인** — `LogSourcePort`로 최근 로그/에러를 읽어와 프롬프트에 주입, 요약·심각도·의심 원인을 구조화된 출력(Pydantic 파서)으로 반환한다.
2. **쿼리 생성 체인** — 자연어 질의 → Cypher(Neo4j) 또는 SQL(pgvector) 초안 생성. 대상 스키마(노드 라벨, 테이블 컬럼)는 프롬프트 컨텍스트에 명시적으로 주입해 환각을 줄인다.
3. **안전장치 (필수)** — 생성된 쿼리는 **항상 `QueryDraft`(미실행 상태)로만 반환**하고, 절대 백엔드에서 자동 실행하지 않는다. 실행 여부는 사람이 API 응답을 확인 후 별도 승인 엔드포인트로 트리거한다. (파괴적 작업 자동화 금지 원칙)
4. **성능** — 대량 로그를 매번 전체 스캔하지 않고, 최근 N건/최근 T분 윈도우로 제한한다 ([[003-langchain-harness]] §2 성능 저하 대응).

```python
# adapter/outbound/langchain/query_generation_chain.py
class QueryGenerationChain(QueryChainPort):
    def __init__(self, llm: BaseChatModel, schema_context: str):
        self._llm = llm
        self._schema_context = schema_context  # Neo4j 라벨/관계 스키마 요약

    async def draft(self, natural_language_query: str) -> QueryDraft:
        chain = QUERY_GEN_PROMPT | self._llm | QueryDraftOutputParser()
        return await chain.ainvoke({
            "schema": self._schema_context,
            "question": natural_language_query,
        })
```

---

## 4. 체크리스트

- [ ] `summarize_alerts()`와 `draft_query()`가 별도 메서드로 분리되어 있는가? (ISP)
- [ ] 생성된 쿼리가 자동 실행되지 않고 `QueryDraft`로만 반환되는가?
- [ ] 로그 조회 범위가 시간/건수로 제한되어 있는가? (성능)
- [ ] 스키마 컨텍스트(Neo4j 라벨 등)를 프롬프트에 명시적으로 주입해 환각을 줄였는가?
- [ ] `python main.py` 기동 후 실제 요약·쿼리 생성 응답을 확인했는가?

---

*이 문서는 LangChain 고객 사례(Elastic)를 근거로 한 구현 전략이며, 실제 Elastic 시스템 내부 구조를 재현한 것이 아니다.*

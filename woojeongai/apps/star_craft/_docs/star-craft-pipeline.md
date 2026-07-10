---
type: hub
app: star_craft
links: []
---

# star_craft 허브 파이프라인 전략

## 개요

`star_craft`는 스타 토폴로지의 **허브**다. 모든 스포크 앱은 이 허브를 경유해 통신한다.  
허브의 두 핵심 책임을 두 개의 DB가 각각 담당한다.

| 책임 | DB | 역할 |
|------|-----|------|
| 전역 온톨로지 인덱스 | **Neo4j** (Graph DB) | 앱 노드·관계 저장, Cypher 탐색 |
| 컨텍스트 라우팅 | **pgvector** (PostgreSQL + pgvector) | 질문 임베딩 유사도 검색 → 타겟 스포크 식별 |

---

## DB 선택 근거

### Graph DB — Neo4j

- 스포크 앱을 **노드**, 앱 간 의존 관계를 **엣지**로 표현하기에 적합
- Cypher 쿼리로 허브→스포크, 스포크→허브 경로를 직관적으로 탐색
- `neo4j` Python 드라이버가 async 지원

### Vector DB — pgvector (PostgreSQL + pgvector)

- 별도 벡터 DB 없이 **기존 PostgreSQL에서 벡터 검색**까지 처리 — 인프라 단순화
- `pgvector/pgvector:pg17` Docker 이미지, SQLAlchemy async와 직접 연동
- `asyncpg` + SQLAlchemy로 코사인 유사도 쿼리 (`<=>` 연산자) 실행
- 사용자 질문을 임베딩해 가장 유사한 스포크 컨텍스트를 찾는 **라우팅 판단**에 사용

---

## Docker 설정 추가

`docker-compose.yaml`에 아래 두 서비스를 추가한다.

```yaml
  neo4j:
    image: neo4j:5
    ports:
      - "7474:7474"   # Browser UI
      - "7687:7687"   # Bolt (드라이버 접속)
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
    volumes:
      - neo4j_data:/data

  pgvector:
    image: pgvector/pgvector:pg17
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=ragtailor
    volumes:
      - pgvector_data:/var/lib/postgresql/data

volumes:
  neo4j_data:
  pgvector_data:
```

`.env` 추가 항목:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ragtailor
```

---

## 헥사고날 아키텍처 내 위치

```
star_craft/
├── app/
│   └── ports/output/
│       ├── graph_repository_port.py    # Neo4j 출력 포트 (인터페이스)
│       └── vector_repository_port.py      # pgvector 출력 포트 (인터페이스)
├── adapter/
│   └── outbound/
│       ├── neo4j_graph_repository.py      # Neo4j 어댑터 (구현체)
│       └── pgvector_vector_repository.py  # pgvector 어댑터 (구현체)
└── dependencies/
    └── __init__.py                     # DI: 포트 ↔ 어댑터 바인딩
```

의존성 방향 준수: `adapter/outbound` → `app/ports/output` → `app/use_cases`

---

## 파이프라인 흐름

```
[inbound API 요청]
        │
        ▼
[use_case: ContextRoutingUseCase]
        │
        ├─ (1) VectorRepositoryPort.search(query_embedding)
        │         └─ pgvector (<=> 연산자) → 유사 컨텍스트 스포크 후보 반환
        │
        ├─ (2) GraphRepositoryPort.get_spoke_path(candidates)
        │         └─ Neo4j Cypher → 허브↔스포크 관계 확인, 최적 경로 결정
        │
        └─ (3) 타겟 스포크 유스케이스 호출 (hub → spoke)
```

### 단계별 설명

**Step 1 — 벡터 유사도 검색**
- 사용자 질문을 임베딩 (exaone3.5:2.4b 또는 Gemini)
- pgvector `<=>` 연산자로 코사인 유사도 Top-K 스포크 후보 반환

**Step 2 — 그래프 경로 확인**
- Neo4j에서 후보 스포크 노드의 상태·관계 조회
- 비활성 노드, spoke↔spoke 직접 연결 시도 등 금지 관계 필터링

**Step 3 — 스포크 디스패치**
- 결정된 스포크의 유스케이스를 허브가 직접 호출
- 결과를 허브가 취합해 응답

---

## 의존성 추가

`requirements.txt`에 추가:

```
neo4j==5.*           # Graph DB 드라이버 (async 지원)
pgvector             # SQLAlchemy용 pgvector 타입 지원
```

---

## Neo4j 온톨로지 스키마

```cypher
// 노드: 스포크 앱
CREATE (:Spoke {name: 'silicon_valley', status: 'active'})
CREATE (:Spoke {name: 'kingsman',       status: 'active'})

// 허브 노드
CREATE (:Hub {name: 'star_craft'})

// 관계: spoke → hub (허용)
MATCH (s:Spoke {name: 'silicon_valley'}), (h:Hub)
CREATE (s)-[:CONNECTS_TO]->(h)

// 관계: hub → spoke (허용)
MATCH (h:Hub), (s:Spoke {name: 'silicon_valley'})
CREATE (h)-[:ORCHESTRATES]->(s)
```

---

## pgvector 테이블 스키마

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE spoke_contexts (
    id          SERIAL PRIMARY KEY,
    spoke       TEXT NOT NULL,
    description TEXT,
    keywords    TEXT[],
    embedding   vector(1024)   -- exaone3.5:2.4b 임베딩 차원
);

-- 코사인 유사도 인덱스
CREATE INDEX ON spoke_contexts
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 구현 순서

```
1. docker-compose에 neo4j, pgvector 서비스 추가        → 검증: 두 컨테이너 정상 기동
2. .env에 접속 정보 추가, core/config.py 반영          → 검증: 환경변수 로드 확인
3. requirements.txt에 neo4j, pgvector 추가             → 검증: pip install 성공
4. 출력 포트 인터페이스 작성 (ports/output/)           → 검증: 추상 메서드 정의
5. 어댑터 구현체 작성 (adapter/outbound/)              → 검증: 단위 테스트 통과
6. DI 바인딩 (dependencies/)                           → 검증: FastAPI 의존성 주입 확인
7. ContextRoutingUseCase 작성                          → 검증: 통합 테스트 (실제 DB 연결)
```

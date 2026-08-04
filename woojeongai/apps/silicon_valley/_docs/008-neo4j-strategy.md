# 008 — Neo4j Docker 설치 전략 (silicon_valley)

> [[004-langgraph-harness]]의 REASONING 노드(`retrieve_graph_context`)가 실제로 조회할 Neo4j 인스턴스를
> 컨테이너로 준비·정합화하는 전략이다. 그래프 조회 로직 자체의 행동 규칙은 [[004-langgraph-harness]],
> LangChain 공통 규칙은 [[003-langchain-harness]]를 따른다. 인프라 전반(SSH·Cloudflare 등) 배경은
> [[../../../../_docs/infra-handoff|infra-handoff.md]] 참고.

---

## 0. 범위 — "신규 설치"가 아니라 "정합화"다

저장소 루트 `docker-compose.yaml`(113~126행)에 `neo4j:5` 서비스가 **이미 정의되어 있다** (`main`,
`friend` 브랜치 동일, `infra-handoff.md`에도 `friend2`에서 구동·검증 완료로 기록됨). 따라서 이 문서는
"Neo4j를 처음 도커로 설치하는 법"이 아니라, **이미 떠 있는 컨테이너를 004-langgraph-harness가 요구하는
조회 경로와 실제로 이어 붙이는 전략**이다.

```yaml
# docker-compose.yaml (현재, 113~126행)
neo4j:
  image: neo4j:5
  container_name: neo4j_container
  ports:
    - "7474:7474"   # Browser UI
    - "7687:7687"   # Bolt
  volumes:
    - neo4j_data:/data
  environment:
    - NEO4J_AUTH=neo4j/1234
    - NEO4J_dbms_security_auth__minimum__password__length=4
  networks: [woojeongalex_net]
  restart: unless-stopped
```

---

## 1. 현재 상태 진단 (Gap Analysis)

| 항목 | 현재 상태 | 문제 |
|------|-----------|------|
| 컨테이너 정의 | 이미 존재, 정상 구동 검증됨 | 자격증명이 `NEO4J_AUTH=neo4j/1234`로 **하드코딩** — 같은 파일의 `pgvector`/`redis`/`pgadmin`은 전부 `${POSTGRES_PASSWORD}` 등 `.env` 변수를 참조하는데 `neo4j`만 패턴이 다르다 |
| 루트 `.env` | `NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD` 항목 없음 | `star_craft/dependencies/graph_qa_provider.py:14-16`가 `os.getenv("NEO4J_URI", "")` 등으로 읽지만 실제로는 항상 빈 문자열이 반환된다 — 컨테이너는 떠 있어도 백엔드가 접속 정보를 모른다 |
| Keymaker 통합 | 없음 — `os.getenv` 직접 호출 | 최근 S3Manager가 "Keymaker 기반 자격증명 로딩"으로 정리된 것과 달리, Neo4j만 자격증명 관리 컨벤션에서 벗어나 있다. `core/matrix/secret_manager.py:67-70`에 이미 범용 `Keymaker.get_secret(name, default)`가 있어 새 메서드 없이 바로 재사용 가능 |
| Healthcheck | 없음 (`backend`는 있음, 4~18행) | `depends_on: condition: service_healthy`를 걸 수 없어, LangGraph reasoning 노드가 뜨기 전에 Neo4j가 준비됐는지 보장할 방법이 없다 |
| `.env` 파일 위치 | 루트 `.env`만 고려됨 | `Keymaker`는 `default_backend_env_path()`(`core/matrix/secret_manager.py:10-12`)로 **`woojeongai/.env`** 를 읽는다. `docker compose`는 **저장소 루트** `.env`를 읽는다(`infra-handoff.md` 알려진 제약사항 7번과 동일한 "두 곳 다 채워야 하는" 문제) |
| APOC 플러그인 | 미설치 | `neo4j-graphrag==1.18.0`(이미 `requirements.txt`에 있음)의 스키마 조회·하이브리드 검색 유틸 일부가 APOC 프로시저를 전제로 하는 경우가 있다 |

---

## 2. 전략

### 2.1 자격증명 파라미터화 — 다른 서비스와 패턴 통일

```yaml
# docker-compose.yaml — neo4j 서비스 (변경안)
neo4j:
  image: neo4j:5
  container_name: neo4j_container
  ports:
    - "7474:7474"
    - "7687:7687"
  volumes:
    - neo4j_data:/data
  env_file:
    - ./.env
  environment:
    - NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD}
  healthcheck:
    test: ["CMD-SHELL", "wget -O /dev/null -q http://localhost:7474 || exit 1"]
    interval: 15s
    timeout: 5s
    retries: 10
    start_period: 20s
  networks: [woojeongalex_net]
  restart: unless-stopped
```

- `NEO4J_dbms_security_auth__minimum__password__length=4`는 개발 편의용 완화 설정이었다 — `.env`
  값이 충분히 긴 비밀번호를 쓰면 굳이 최소 길이를 낮출 필요가 없으므로 제거한다. (운영 전환 시
  약한 비밀번호를 다시 쓰는 실수를 구조적으로 막는다.)
- `healthcheck`는 Neo4j 공식 이미지 관례대로 인증 없이 접근 가능한 7474(Browser HTTP)에 대해
  체크한다 — 비밀번호를 healthcheck 커맨드 라인에 노출하지 않기 위함.

### 2.2 `.env` 항목 추가 — **두 위치 모두**

`infra-handoff.md` 알려진 제약사항 7번과 동일한 이유로, 아래 세 변수를 **루트 `.env`와
`woojeongai/.env` 양쪽에 모두** 추가한다 (docker compose는 루트를, `Keymaker`는
`woojeongai/.env`를 읽으므로 한쪽만 채우면 다른 한쪽이 빈 문자열로 남는다).

```bash
# .env (루트) 및 woojeongai/.env — 개발용 예시값, 운영 전환 시 반드시 교체
NEO4J_USER=neo4j
NEO4J_PASSWORD=<강한 비밀번호로 교체>
# 컨테이너 밖(WSL에서 python main.py로 직접 백엔드 실행)에서 접속할 때
NEO4J_URI=bolt://localhost:7687
```

- **접속 문자열은 실행 위치에 따라 달라진다** — woojeongai/CLAUDE.md §1의 "로컬: `python main.py`"
  방식(컨테이너 밖 실행)에서는 `bolt://localhost:7687`, 반대로 `backend` 컨테이너 **안에서** 접속할
  경우(docker-compose로 backend까지 띄운 상태)는 같은 네트워크(`woojeongalex_net`)의 서비스명을
  써서 `bolt://neo4j:7687`이 되어야 한다. 둘 중 어느 쪽으로 백엔드를 띄우는지에 맞춰 값을 바꾼다.
- `.env`는 `.gitignore`에 이미 등록되어 있다 — 이 문서·커밋에는 실제 비밀번호를 절대 적지 않는다
  (`infra-handoff.md` 보안 주의사항과 동일 원칙, 저장소가 Public이기 때문).

### 2.3 Keymaker 경유로 정렬 — `os.getenv` 직접 호출 제거

```python
# star_craft/dependencies/graph_qa_provider.py — 변경 방향
from core.matrix.keymaker_api import Keymaker, get_keymaker

def get_graph_query_repository(
    keymaker: Keymaker = Depends(get_keymaker),
) -> GraphQueryPort:
    return Neo4jGraphQueryRepository(
        uri=keymaker.get_secret("NEO4J_URI"),
        user=keymaker.get_secret("NEO4J_USER"),
        password=keymaker.get_secret("NEO4J_PASSWORD"),
    )
```

`Keymaker.get_secret()`은 이미 범용으로 존재하므로(§1) 새 메서드를 추가하지 않고 그대로 재사용한다.
silicon_valley에 [[004-langgraph-harness]] §1의 `GraphQueryPort`를 구현할 때도 동일하게 이 경유
방식을 따른다 — `os.getenv`를 provider/director에 직접 쓰지 않는다.

### 2.4 APOC 플러그인 추가 (GraphRAG 대비)

```yaml
environment:
  - NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD}
  - NEO4J_PLUGINS=["apoc"]
```

`neo4j-graphrag` 라이브러리로 Text-to-Cypher/하이브리드 검색을 구현할 때 일부 유틸이 APOC 프로시저를
사용한다. 지금 당장 필요하지 않다면 미루되, [[002-neo4j-harness]](GraphRAG 적재 규칙, 현재 미작성)를
채울 때 실제로 필요해지면 이 항목부터 켠다 — 미리 켜두는 것 자체는 부작용이 없다.

### 2.5 리소스 튜닝 (운영 단계, 선택)

개발 단계에서는 기본값으로 충분하다. LangGraph reasoning 노드가 다단계(Multi-hop) 탐색을 자주
실행하게 되면 아래 항목을 관찰 후 조정한다 — 지금 단계에서 미리 값을 못박지 않는다.

```yaml
environment:
  - NEO4J_server_memory_heap_max__size=1G
  - NEO4J_server_memory_pagecache_size=512M
```

### 2.6 보안 — 운영 전환 시 반드시 할 것

- `NEO4J_AUTH=neo4j/1234`(현재 하드코딩된 값)는 개발용 더미 비밀번호다. §2.2로 파라미터화한 뒤,
  운영 배포 전 `.env`의 `NEO4J_PASSWORD`를 새로 발급한 강한 값으로 교체한다.
  (`infra-handoff.md` "friend2의 `.env`는 개발용 임시값" 경고와 동일한 원칙)
- 이 저장소는 Public이므로, 이 문서를 포함해 어떤 커밋에도 실제 비밀번호·토큰을 남기지 않는다.

---

## 3. [[004-langgraph-harness]]와의 연결

- `retrieve_graph_context` 노드가 주입받는 `GraphQueryPort` 구현체(`Neo4jGraphQueryRepository`)는
  이 컨테이너의 Bolt 포트(7687)에 접속한다 — 접속 문자열은 §2.2 기준.
- 004 §2.9(로컬 검증) 체크리스트를 통과하려면, `python main.py` 기동 **전에** 이 문서 §2.1~§2.3이
  먼저 적용되어 있어야 한다 — 컨테이너가 떠 있어도 `.env`/Keymaker 배선이 안 되어 있으면
  `Neo4jGraphQueryRepository.find_related_context()`가 빈 URI로 `RuntimeError`를 낸다
  (`neo4j_graph_query_repository.py`의 기존 방어 로직, 의도된 동작).
- 004 §2.7(모델 교체 가능성)과 동일하게, Neo4j 접속 정보도 하드코딩하지 않고 Director/provider에서
  주입한다 — §2.3이 그 적용이다.

---

## 4. 체크리스트

- [ ] `docker-compose.yaml`의 `neo4j` 서비스가 `${NEO4J_USER}`/`${NEO4J_PASSWORD}`를 참조하는가? (하드코딩 제거)
- [ ] `healthcheck`가 추가되어 `docker compose ps`에서 `healthy`로 뜨는가?
- [ ] 루트 `.env`와 `woojeongai/.env` **양쪽 모두**에 `NEO4J_USER`/`NEO4J_PASSWORD`/`NEO4J_URI`가 있는가?
- [ ] `graph_qa_provider.py`(및 silicon_valley에 새로 만들 provider)가 `os.getenv` 대신 `Keymaker.get_secret()`을 쓰는가?
- [ ] 백엔드를 컨테이너 안에서 띄우는지 밖에서 띄우는지에 맞춰 `NEO4J_URI`가 `neo4j:7687` 또는 `localhost:7687`로 올바르게 설정되었는가?
- [ ] 운영 배포 전 더미 비밀번호(`neo4j/1234`)를 교체했는가?
- [ ] `docker compose up -d neo4j` 후 `http://localhost:7474` 접속 및 `cypher-shell`/Bolt 접속을 실제로 확인했는가?

---

*이 문서는 이미 구동 검증된 기존 Neo4j 컨테이너 정의(`docker-compose.yaml`)를 [[004-langgraph-harness]]가
요구하는 조회 경로에 맞춰 정합화하는 전략이며, Neo4j/Docker Compose 자체의 API 문서가 아니다.*
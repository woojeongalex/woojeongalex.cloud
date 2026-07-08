# CLAUDE.md — 백엔드 (woojeongai) 인수인계

> 전역 원칙·행동 하네스 → `woojeongai/_claude/CLAUDE.md`
> Titanic 앱 상세 → `apps/titanic/_docs/CLAUDE.md`

---

## 0. 문서 읽는 순서 (백엔드)

| 순서 | 문서 | 역할 |
|------|------|------|
| 1 | **본 파일** `woojeongai/CLAUDE.md` | 백엔드 인수인계 정본 |
| 3 | `vault/woojeongai/backend_rules.md` | FastAPI·DB·로깅·API 경로 |
| 4 | `vault/woojeongai/fastapi_rules.md` | FastAPI 초기 설정 규칙 |
| 5 | `vault/woojeongai/app-rules.md` | 클린 아키텍처·SOLID·ISP 상세 |
| 6 | `vault/woojeongai/db-rules.md` | ORM PK·`id`·refresh 규칙 |
| 7 | [[woojeongai/apps/titanic/_docs/CLAUDE\|`apps/titanic/_docs/CLAUDE.md`]] | Titanic 레퍼런스 앱 상세 |

**우선순위 (충돌 시):** 사용자 지시 > `vault/` > 본 파일 > `../CLAUDE.md`

---

## 1. 저장소 레이아웃

```
woojeongai/
  main.py                      # FastAPI 앱 · include_router · init_db · lifespan
  requirements.txt             # Python 의존성
  logging_setup.py             # 도메인별 로거 등록
  alembic.ini                  # DB 마이그레이션 설정
  apps/
    friday13th/                # 인증 (signup/login)
    music/                     # 보컬·MR·악기·스피치·비디오
    titanic/                   # James(업로드) / Walter(조회) 레퍼런스
  core/
    matrix/
      keymaker_api.py          # API 키 관리
  alembic/versions/            # 마이그레이션 스크립트
```

- 작업 루트: `woojeongai/apps/<앱명>/`
- `PYTHONPATH`에 `woojeongai/apps` 포함 (`uvicorn main:app`, `python main.py`)
- 로컬: `cd woojeongai` → `python main.py` (포트 8000, reload)

---

## 2. 기술 스택

| 항목 | 버전 |
|------|------|
| FastAPI | 0.136.1 |
| SQLAlchemy | 2.0 (async) |
| SQLModel | 0.0.38 |
| asyncpg | 0.30.0 |
| Alembic | 1.18.4 |
| pandas | 3.0.3 |
| scikit-learn | 1.8.0 |
| librosa | 0.11.0 |
| moviepy | 2.2.1 |
| google-generativeai | 0.8.6 (Gemini) |
| ollama | 0.6.2 (로컬 LLM 폴백) |
| bcrypt | 4.2.1 |
| pytest + pytest-asyncio | 8.3.5 + 0.24.0 |

---

## 3. 클린 아키텍처 + 헥사고날 (Ports & Adapters)

### 3.1 의존성 규칙

- 의존성은 **안쪽(도메인·Use Case)** 으로만 향한다.
- **Use Case / Interactor** 는 `adapter/`·ORM·FastAPI Request/Response **import 금지**.
- HTTP·DB 변환은 **Adapter 경계에서 1회** (mapper / parser / handler).

### 3.2 4계층

| 계층 | 위치 | 책임 |
|------|------|------|
| **Entities** | `domain/entities/`, `domain/value_objects/` | 순수 비즈니스 (프레임워크 무관) |
| **Use Cases** | `app/use_cases/*_interactor.py` | 오케스트레이션, Port만 의존 |
| **Interface Adapters** | `adapter/inbound/`, `adapter/outbound/` | HTTP·ORM·외부 I/O |
| **Frameworks** | FastAPI, SQLAlchemy, SQLModel, Neon PG | `main.py`, `core/` |

### 3.3 프렉탈(Fractal) 디렉터리 — 모든 앱 공통

```
<app>/
  domain/
    entities/
    value_objects/
  app/
    dtos/                      # Use Case 입출력 (frozen dataclass)
    ports/
      input/                   # *UseCase (ABC) — inbound Port
      output/                  # *RepositoryPort (ABC) — outbound Port
    use_cases/
      *_interactor.py          # input Port 구현 (구 명칭 *Service 지양)
  dependencies/
    *_director.py              # DIP 조립소 (FastAPI Depends 팩토리)
  adapter/
    inbound/
      api/
        deps/                  # get_*_use_case re-export
        v1/                    # *_router.py (thin)
        schemas/               # Pydantic Request/Response
        mappers/               # schema ↔ dto
        parsers/               # UploadFile → 내부 타입 (무상태)
        handlers/              # HTTP 예외·DB 오류 매핑
    outbound/
      orm/                     # SQLAlchemy 2.0 Mapped 스타일
      pg/                      # *PgRepository
```

**헥사고날 관점**

- **Inbound Port** = `app/ports/input/*_use_case.py`
- **Outbound Port** = `app/ports/output/*_repository_port.py`
- **Driving Adapter** = router, parser, mapper, handler
- **Driven Adapter** = `*_pg_repository`, ORM

---

## 4. SOLID — 저장소 적용 규칙

### S — Single Responsibility (단일 책임)

| 모듈 | 변경 이유 하나 |
|------|----------------|
| `*_router.py` | HTTP 경로·스키마·Use Case 위임 |
| `*_interactor.py` | 애플리케이션 규칙·흐름 |
| `*_pg_repository.py` | 영속화 (INSERT/SELECT/commit) |
| `*_inbound_mapper.py` | schema ↔ dto 변환 |
| `*_csv_parser.py` / `video_upload_parser.py` | 파일 파싱만 |
| `*_inbound_handlers.py` | ValueError/SQLAlchemyError → HTTPException |

**금지:** 라우터에 `select`, `commit`, 비즈니스 `if` 분기, Repository 직접 생성.

### O — Open/Closed (개방-폐쇄)

새 타입 추가 시 기존 코드를 열지 않고 새 클래스·테이블 항목만 추가한다.

```python
# ❌ if/elif 타입 분기
def map_error(exc):
    if "429" in str(exc): ...
    if "404" in str(exc): ...

# ✅ 규칙 테이블 — 새 케이스는 튜플에 항목만 추가
@dataclass(frozen=True)
class _ErrorRule:
    keywords: tuple[str, ...]
    status_code: int
    detail: str

_ERROR_RULES: tuple[_ErrorRule, ...] = (
    _ErrorRule(keywords=("429", "quota"), status_code=429, detail="..."),
    _ErrorRule(keywords=("404", "not found"), status_code=502, detail="..."),
)
```

### I — Interface Segregation (ISP) — **핵심**

- 클라이언트가 쓰는 메서드만 Port에 둔다.
- **Fat Interface 금지** — `pass`, `NotImplemented`, 항상 `[]` 반환 = 분리 신호.
- **James ↔ Walter 분리** (Titanic 정본):

| Port | 메서드 | 하지 않는 것 |
|------|--------|--------------|
| `JamesUseCase` | `upload` | 조회·페이지네이션 |
| `WalterUseCase` | `read_passengers` | 업로드 |

- 메서드명: **짧은 동사** (`upload`, `read`, `search`, `analyze`)
  ❌ `receive_uploaded_records`, `search_and_persist`

### D — Dependency Inversion (DIP) — **Director 패턴**

```python
# dependencies/james_director.py (정본)
def get_james_repository(db: AsyncSession = Depends(get_db)) -> JamesRepositoryPort:
    return JamesPgRepository(session=db)

def get_james_use_case(
    repository: JamesRepositoryPort = Depends(get_james_repository),
) -> JamesUseCase:
    return JamesInteractor(repository=repository)
```

```python
# adapter/inbound/api/deps/titanic_deps.py — re-export만
from titanic.dependencies.james_director import get_james_use_case
from titanic.dependencies.walter_director import get_walter_use_case
```

**FastAPI Depends 주입 규칙**

- `Depends()`는 **라우터 함수 파라미터**에서만 동작한다.
- 클래스 `__init__`의 인스턴스 변수(`self.x = Depends(...)`)에는 주입 불가.

```python
# ❌ 클래스 속성에 Depends — FastAPI가 스캔하지 않음
class MyView:
    jack: JackUseCase = Depends(get_jack_use_case)  # 절대 금지

# ✅ 라우터 파라미터
@router.post("/")
async def endpoint(jack: JackUseCase = Depends(get_jack_use_case)):
    ...

# ✅ CBV 패턴 — __init__ 파라미터
class MyView:
    def __init__(self, jack: JackUseCase = Depends(get_jack_use_case)):
        self.jack = jack
```

---

## 5. FastAPI 패턴 (Thin Router)

### 5.1 업로드 + 파서 패턴 (James)

```python
@james_router.post("/upload", response_model=JamesUploadResponse)
async def upload_titanic_csv(
    file: UploadFile = File(...),
    james: JamesUseCase = Depends(get_james_use_case),
) -> JamesUploadResponse:
    file_name, rows = await read_james_upload(file)
    result = await james.upload(james_schemas_to_person_commands(rows), file_name)
    return JamesUploadResponse(**result)
```

### 5.2 조회 패턴 (Walter)

```python
@walter_router.get("/passengers", response_model=WalterPassengerPageResponse)
async def read_passengers(
    source_file: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    walter: WalterUseCase = Depends(get_walter_use_case),
) -> WalterPassengerPageResponse:
    page_dto = await walter.read_passengers(source_file, page, size)
    return walter_page_dto_to_response(page_dto)
```

### 5.3 데이터 흐름 (한 요청)

```
HTTP Request
  → router (스키마 바인딩)
  → parser (파일 업로드 시)
  → mapper (schema → Command/DTO)
  → handler (선택: DB/검증 예외)
  → UseCase/Interactor (Port 타입)
  → Repository Port 구현 (*PgRepository)
  → ORM → DB
  → mapper (Result DTO → Response schema)
  → HTTP Response
```

---

## 6. 앱별 현황

### 6.1 Titanic — 레퍼런스 앱

상세: `apps/titanic/_docs/CLAUDE.md`

James(업로드) / Walter(조회) 패턴 정본. 모든 신규 앱은 이 구조를 따른다.

### 6.2 Music — 6개 도메인

| 도메인 | 쓰기 UseCase | 읽기 UseCase | Director |
|--------|-------------|--------------|----------|
| Evaluation | `upload` | — | `evaluation_director` |
| Search (MR) | — | `search` | `search_director` |
| Suggest | `upload` | `read` | `suggest_director` |
| Instrument | `upload` | `search` (카탈로그) | `instrument_director` |
| Speech | `upload` | `read_topics` | `speech_director` |
| Video | `analyze` (+ parser) | — (DB 없음) | `video_director` |

**deps:** `music/adapter/inbound/api/deps/music_deps.py` — 6개 `get_*_use_case` re-export.

**API 요약**

| 메서드 | 경로 | Use Case |
|--------|------|----------|
| GET | `/api/songs/search?q=` | `SearchUseCase.search` |
| POST | `/api/music/sing-evaluation` | `EvaluationUseCase.upload` |
| POST/GET | `/api/music/vocal-recommendations` | `SuggestUseCase.upload / read` |
| GET | `/api/music/instrument-catalog` | `InstrumentUseCase.search` |
| POST | `/api/music/instrument-evaluation` | `InstrumentUseCase.upload` |
| GET | `/api/music/speech-topics` | `SpeechUseCase.read_topics` |
| POST | `/api/music/speech-evaluation` | `SpeechUseCase.upload` |
| POST | `/api/music/analyze-video` | `VideoAnalysisUseCase.analyze` |

**미완 (3차 마이그레이션 예정)**

- `sing_evaluations.user_id` — ORM에는 있으나 Neon DB에 컬럼 없음 → POST 503
- ERD v2: `user_vocal_recordings.catalog_song_id` 제거 방향

### 6.3 Friday13th — 인증

- `signup_router` / `login_router` → `SignupInteractor` / `LoginInteractor`
- `UserEntity` — `users` 테이블, bcrypt
- `role`은 서버에서 `"user"` 고정

---

## 7. ORM · DB 규칙

- **ORM 스타일: SQLAlchemy 2.0** — `Mapped`, `mapped_column` 사용
  (`Field`, 구 `Column` 방식 금지)
- PK: 정수 `id` 자동 증가
- INSERT 후 `await session.refresh(entity)` 로 `id` 반영
- 세션: 요청 단위 `Depends(get_db)`, Repository에서 commit/rollback
- Windows: event loop 정책은 `main.py` 에서 **한 번만**

```python
# ✅ SQLAlchemy 2.0 Mapped 스타일
class PassengerModel(SQLModel, table=True):
    __tablename__ = "passengers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    survived: Mapped[bool] = mapped_column(default=False)
```

**Repository 번들 (Music 3NF)**

- Evaluation: `sing_evaluations` → `user_vocal_recordings` → `ai_vocal_analyses` 한 트랜잭션
- Instrument/Speech: `pg_bundle_repository.save_three_part_bundle` 공통

---

## 8. 로깅

- 도메인 흐름: **레이어당 1줄** INFO (동일 요청 10줄 이상 금지)
- 로거 등록: `logging_setup.py`
- `print` 디버그 커밋 금지
- Titanic: `titanic_flow_log` — adapter·usecase·outbound 레이어만 (`ports`는 로그 태그 금지)

---

## 9. 코딩 규칙

- **코드만 출력** — 설명·주석 불필요 시 생략
- **수정 범위 엄수** — 지시한 파일·부분만 수정, 임의 리팩터링 금지
- 같은 패턴 파일 수정 시 동일 패턴의 모든 파일을 찾아 일괄 점검·적용
- `dependencies/` 파일: `get_repository` + `get_use_case` 두 함수 **반드시 분리**

---

## 10. 코딩·리뷰 체크리스트

- [ ] Use Case가 `adapter.inbound` 스키마를 import 하지 않는가?
- [ ] Router가 Repository / `get_db` / Interactor 구현을 import 하지 않는가?
- [ ] Port 메서드가 **한 역할·짧은 동사**인가? (ISP)
- [ ] Fat Interface / 미사용 abstract 메서드 없는가?
- [ ] 조립이 `dependencies/*_director.py` 또는 `deps/`에만 있는가?
- [ ] schema ↔ dto 변환이 mapper에서 1회인가?
- [ ] `Depends()`가 라우터 파라미터에만 있는가?
- [ ] diff가 사용자 요청 범위만 포함하는가?

---

## 11. 안티패턴 (하지 말 것)

```python
# ❌ 라우터에서 Repository 직접 조립
def _use_case(db):
    return EvaluationService(EvaluationRepository(db))

# ❌ Use Case에서 ORM Entity를 HTTP body로 직접 수신
async def save_evaluation(self, body: VocalEvaluationCreateRequest): ...

# ❌ Port에 쓰기+읽기 한꺼번에 (ISP 위반)
class TitanicRepository(ABC):
    async def upload(...): ...
    async def read_passengers(...): ...
    async def train_model(...): ...

# ❌ 클래스 속성에 Depends
class Router:
    use_case: UseCase = Depends(get_use_case)  # 절대 금지

# ❌ dependencies/에서 get_repository + get_use_case 미분리
def get_use_case(db: AsyncSession = Depends(get_db)) -> UseCase:
    return Interactor(PgRepository(session=db))  # 분리해야 함
```

---

## 12. 신규 기능 추가 절차

1. **Port** 정의 — `app/ports/input/`, `app/ports/output/` (ISP: 메서드 최소)
2. **DTO** — `app/dtos/` (frozen dataclass)
3. **Interactor** — `app/use_cases/*_interactor.py`
4. **PgRepository** — `adapter/outbound/pg/*_pg_repository.py`
5. **ORM** — `adapter/outbound/orm/` (+ `main.py` import 등록)
6. **Director** — `dependencies/*_director.py` (get_repository + get_use_case 분리)
7. **deps re-export** — `adapter/inbound/api/deps/`
8. **schemas + mapper** (+ parser if upload, + handler if DB errors)
9. **thin router** — `adapter/inbound/api/v1/`
10. **`main.py`** `include_router`
11. **Alembic migration** (테이블/컬럼 변경 시)
12. **검증** — `python main.py` 기동, curl/requests

---

---

## 13. async / def 선택 규칙 — CPU-bound vs I/O-bound

| 성격 | 예시 | Port 선언 | 구현 |
|------|------|-----------|------|
| I/O-bound | DB 조회, LLM API, 파일 읽기 | `async def` | `async def` + `await` |
| CPU-bound | Kiwi 형태소 분석, 수치 계산 | `def` | `def` (동기) |

**핵심 원칙**

- `async def`는 비블로킹을 **보장하지 않는다**. 내부가 CPU 연산이면 이벤트 루프를 그대로 블로킹한다.
- CPU-bound 메서드에 `async`를 붙이면 비블로킹인 것처럼 **오해를 유발**하므로 금지한다.
- Kiwi처럼 처리 시간이 길어질 수 있는 CPU 작업이 실제로 이벤트 루프를 막을 경우, 메서드 시그니처를 바꾸는 게 아니라 **호출 측에서 스레드풀로 넘긴다**.

```python
# ✅ Port: CPU-bound는 def
class AndrewsArchitectUseCase(ABC):
    def analyze_intent(self, question: str) -> dict:  # async 붙이지 않음
        pass

# ✅ Interactor: 동기 구현
def analyze_intent(self, question: str) -> dict:
    tokens = self.kiwi.tokenize(question)
    ...

# ✅ 호출 측(router/interactor)에서 무거울 때만 스레드풀 위임
result = await asyncio.to_thread(self.analyze_intent, question)

# ❌ CPU-bound에 async 붙이기 — 비블로킹처럼 보이지만 실제론 블로킹
async def analyze_intent(self, question: str) -> dict:
    tokens = self.kiwi.tokenize(question)  # 이벤트 루프 블로킹
    ...
```

---

*세부 규칙 변경 시 `vault/woojeongai/` 문서를 먼저 갱신하고, 본 파일 §6을 맞춰 업데이트한다.*

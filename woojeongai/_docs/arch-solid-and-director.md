# SOLID 원칙 & Director 패턴

## S — Single Responsibility (단일 책임)

| 모듈 | 변경 이유 하나 |
|------|----------------|
| `*_router.py` | HTTP 경로·스키마·Use Case 위임 |
| `*_interactor.py` | 애플리케이션 규칙·흐름 |
| `*_pg_repository.py` | 영속화 (INSERT/SELECT/commit) |
| `*_inbound_mapper.py` | schema ↔ dto 변환 |
| `*_csv_parser.py` / `video_upload_parser.py` | 파일 파싱만 |
| `*_inbound_handlers.py` | ValueError/SQLAlchemyError → HTTPException |

**금지:** 라우터에 `select`, `commit`, 비즈니스 `if` 분기, Repository 직접 생성.

## O — Open/Closed (개방-폐쇄)

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

## I — Interface Segregation (ISP) — 핵심

- 클라이언트가 쓰는 메서드만 Port에 둔다.
- **Fat Interface 금지** — `pass`, `NotImplemented`, 항상 `[]` 반환 = 분리 신호.
- **James ↔ Walter 분리** (Titanic 정본):

| Port | 메서드 | 하지 않는 것 |
|------|--------|--------------|
| `JamesUseCase` | `upload` | 조회·페이지네이션 |
| `WalterUseCase` | `read_passengers` | 업로드 |

- 메서드명: **짧은 동사** (`upload`, `read`, `search`, `analyze`)
  ❌ `receive_uploaded_records`, `search_and_persist`

## D — Dependency Inversion (DIP) — Director 패턴

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

### FastAPI Depends 주입 규칙

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

### dependencies/ 규칙

`get_repository` + `get_use_case` 두 함수 **반드시 분리**

```python
# ❌ 한 함수에서 직접 조립
def get_use_case(db: AsyncSession = Depends(get_db)) -> UseCase:
    return Interactor(PgRepository(session=db))  # 분리해야 함

# ✅ 분리
def get_repository(db: AsyncSession = Depends(get_db)) -> RepositoryPort:
    return PgRepository(session=db)

def get_use_case(repo: RepositoryPort = Depends(get_repository)) -> UseCase:
    return Interactor(repository=repo)
```

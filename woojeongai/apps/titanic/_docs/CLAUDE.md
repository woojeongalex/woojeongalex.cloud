# CLAUDE.md — Titanic 앱 (레퍼런스)

> 백엔드 허브 → [[woojeongai/CLAUDE|`woojeongai/CLAUDE.md`]]

Titanic은 **James(업로드) / Walter(조회) 분리 패턴**의 정본이다.  
신규 앱을 추가할 때 이 구조를 그대로 복제한다.

---

## 1. 파일 구조

| 역할 | 파일 | 비고 |
|------|------|------|
| 업로드 (James) | `james_router`, `james_interactor`, `james_pg_repository` | CSV → `upload` |
| 조회 (Walter) | `walter_router`, `walter_interactor`, `walter_pg_repository` | `read_passengers` |
| DIP 조립 | `dependencies/james_director.py` | `get_james_use_case` |
| DIP 조립 | `dependencies/walter_roaster.py` | `get_walter_use_case` |
| deps re-export | `adapter/inbound/api/deps/titanic_deps.py` | router가 여기만 import |

---

## 2. ISP — James / Walter Port 분리

| Port | 메서드 | 하지 않는 것 |
|------|--------|--------------|
| `JamesUseCase` | `upload` | 조회·페이지네이션 |
| `WalterUseCase` | `read_passengers` | 업로드 |
| `JamesRepositoryPort` | `upload` | read |
| `WalterRepositoryPort` | `read_passengers` | upload |

---

## 3. Director 정본

```python
# dependencies/james_director.py
def get_james_use_case(db: AsyncSession = Depends(get_db)) -> JamesUseCase:
    repository: JamesRepositoryPort = JamesPgRepository(session=db)
    return JamesInteractor(repository=repository)
```

```python
# adapter/inbound/api/deps/titanic_deps.py — re-export만
from titanic.dependencies.james_director import get_james_use_case
from titanic.dependencies.walter_roaster import get_walter_use_case
```

---

## 4. ORM · Alembic

- **ORM:** `person_orm`, `booking_orm`
- James 업로드 시 person + booking **한 트랜잭션** INSERT.
- **Alembic:** `woojeongai/alembic/versions/20260604_0001_titanic_person_booking_tables.py`
- INSERT 후 `await session.refresh(entity)` 로 `id` 반영.

---

## 5. 로깅

- 로거: `titanic_flow_log`
- 태그 사용 레이어: adapter·usecase·outbound **만** (`ports`는 로그 태그 금지)

---

## 6. 레거시 · 주의

| 항목 | 상태 | 조치 |
|------|------|------|
| `PgTitanicUseCaseFactory` | 구형 조립 | `dependencies/*_director` 가 정본 — 점진적 제거 대상 |
| 스텁 PG repo (`@staticmethod`) | 미완성 캐릭터 라우터용 | 해당 캐릭터 구현 시 교체 |
| `walter.introduce_myself` | router에 있으나 Port 미정의 가능 | 잠재 버그 — Port 정의 후 연결 필요 |

---

## 7. 신규 앱 추가 시 복제 순서

1. `apps/<새앱>/` 생성, Titanic 프렉탈 구조 복사
2. Port → DTO → Interactor → PgRepository → ORM → Director → deps → router 순서로 구현
3. `main.py` `include_router` 등록
4. Alembic migration 작성
5. `import main` + curl 로 검증

## 타이타닉 도메인 문서 연결

 * 타이타닉 도메인 문서 연결
 * 타이타닉 피처 정리 : [[titanic-features]]
 * 타이타닉 머신러닝 : [[titanic-machine-learning]]
 * 타이타닉 ERD : [[TITANIC-ERD]]
 * 타이타닉 알고리즘 : [[titanic-algorithm]]
 * 타이타닉 NF : [[titanic-nf]]
 * 
# 엔티티(Entity) 규칙

백엔드 **테이블(ORM)** 정의 시 따르는 공통 규칙이다.  
**적용:** `backend/apps/` 이하 엔티티·마이그레이션·수동 DDL.  
**상위 문서:** [BACKEND_RULES.md](./BACKEND_RULES.md)

이 저장소는 **`database.Base` + SQLAlchemy 2.0 Declarative**(`Mapped`, `mapped_column`)를 기본으로 쓴다. 신규 테이블을 **SQLModel**로 둘 경우에도 아래 **기본 키 규칙**은 동일하다.

---

## 기본 키: `id` (int, 자동 증감)

**모든 테이블은 반드시 `int` 타입의 기본 키를 갖는다.** 컬럼·필드 이름은 **`id`로 통일**한다.

| 항목 | 규칙 |
|------|------|
| Python 필드명 | `id` |
| DB 컬럼명 | `id` (SQLModel: `sa_column_kwargs={"name": "id"}`) |
| 타입 | SQLModel: `Optional[int]` (INSERT 전 `None`, DB 할당). SQLAlchemy 2: 보통 `Mapped[int]` + `autoincrement=True` |
| 역할 | 시스템 내부용 자동 증감 고유 번호 (PK) |
| `primary_key` | `True` |
| SQLModel `default` | `None` |

비즈니스 식별자(로그인 아이디 `username`, 카탈로그용 문자열 `catalog_song_id` 등)는 **별도 컬럼**으로 두고, **`id`와 혼용하지 않는다.**

---

## 표준 정의 (복사용 템플릿 · SQLModel)

```python
from typing import Optional

from sqlmodel import Field, SQLModel


class Example(SQLModel, table=True):
    __tablename__ = "examples"

    # 1. 시스템 내부용 자동 증감 고유 번호 (기본 키)
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"name": "id"},  # DB 컬럼명: id
    )

    # 2. 이하 비즈니스 필드 ...
```

`autoincrement`를 명시해야 하면 `sa_column=Column(Integer, primary_key=True, autoincrement=True)` 등으로 확장해 동일 정책을 유지한다.

---

## 이 저장소 참조 구현 (SQLModel · SQLAlchemy 2.0)

ORM 엔티티는 **`SQLModel`, `table=True`** (`music/adapter/outbound/orm/`, `friday13th/adapter/outbound/orm/user_model.py` 등) 또는 레거시 Declarative `Base`를 쓴다. 테이블은 `init_db`에서 `SQLModel.metadata` + `Base.metadata` 모두 `create_all` 한다.

- **`friday13th/adapter/outbound/orm/user_model.py`** — `UserEntity`(SQLModel): `users` 테이블. 시스템 PK **`id`**, 로그인 식별자 **`username`**. bcrypt 유틸 `hash_password` / `verify_password` 동일 파일.
- **`music/adapter/outbound/orm/list_model.py`** — `SongMrSearchListEntity`(SQLModel): 시스템 PK `id`, 카탈로그 키 **`catalog_song_id`**
- **`music/adapter/outbound/orm/sing_model.py`** — `SingEvaluationEntity`(SQLModel, `sing_evaluations`): 시스템 PK **`id`**, **`user_id`**(nullable, 세션 소유), **`created_at`** — MR·점수는 **저장하지 않음** (3NF 허브).

SQLModel PK 예시:

```python
id: Optional[int] = Field(default=None, primary_key=True)
```

**주의:** 예시의 **이중 PK(`id` + `userId`)** 는 사용하지 않는다. 비즈니스 식별자는 `username` 등 **별도 컬럼**으로 둔다.

**구 예시 (SQLAlchemy 2 `Mapped`):**

```python
id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
```

---

## 저장 후 `id` 동기화

INSERT 후 DB가 부여한 `id`를 인스턴스에 반영하려면 세션에서 **`refresh`** 를 호출한다.

```python
self.session.add(entity)
await self.session.commit()
await self.session.refresh(entity)  # entity.id 에 자동 증가 값 반영
```

참조:

- `music/adapter/outbound/pg/list_pg_repository.py` — `save_search_results` (다건 `refresh`)
- `music/adapter/outbound/pg/evaluation_pg_repository.py` — 평가 번들 저장 (단건 `refresh`)
- `friday13th/adapter/outbound/pg/signup_pg_repository.py` — `save_user` (단건 `refresh`)

---

## 체크리스트 (신규 테이블)

### SQLModel을 쓸 때

- [ ] `SQLModel`, `table=True` 클래스에 `id` 필드가 있는가?
- [ ] `id`가 `Optional[int]` + `primary_key=True` + `default=None` 인가?
- [ ] DB 컬럼명이 `id`인가? (`sa_column_kwargs={"name": "id"}`)
- [ ] 비즈니스용 고유 식별자를 `id` 대신 별도 필드로 정의했는가?

### SQLAlchemy 2.0 (`Base` 서브클래스)를 쓸 때

- [ ] 정수형 PK 1개, 속성·컬럼명 `id`
- [ ] `primary_key=True`, `autoincrement=True` (또는 DB 시퀀스와 동등한 전략)
- [ ] INSERT 후 `id`가 필요하면 `await session.refresh(instance)` (또는 `flush` 후 조회)

---

## 프론트엔드 (`frontend/`)

ORM은 없다. FastAPI가 내려주는 **DB 행의 정수 PK**는 필드명 **`id`** 로 받는다 (예: `SongMrHit.id`). 비즈니스 키는 별도 필드(`catalog_song_id` 등)로 구분한다.

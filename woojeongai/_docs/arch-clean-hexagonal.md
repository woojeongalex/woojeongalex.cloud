# 클린 아키텍처 + 헥사고날 (Ports & Adapters)

## 의존성 규칙

- 의존성은 **안쪽(도메인·Use Case)** 으로만 향한다.
- **Use Case / Interactor** 는 `adapter/`·ORM·FastAPI Request/Response **import 금지**.
- HTTP·DB 변환은 **Adapter 경계에서 1회** (mapper / parser / handler).

## 4계층

| 계층 | 위치 | 책임 |
|------|------|------|
| **Entities** | `domain/entities/`, `domain/value_objects/` | 순수 비즈니스 (프레임워크 무관) |
| **Use Cases** | `app/use_cases/*_interactor.py` | 오케스트레이션, Port만 의존 |
| **Interface Adapters** | `adapter/inbound/`, `adapter/outbound/` | HTTP·ORM·외부 I/O |
| **Frameworks** | FastAPI, SQLAlchemy, SQLModel, Neon PG | `main.py`, `core/` |

## 프렉탈(Fractal) 디렉터리 — 모든 앱 공통

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

## 헥사고날 관점

- **Inbound Port** = `app/ports/input/*_use_case.py`
- **Outbound Port** = `app/ports/output/*_repository_port.py`
- **Driving Adapter** = router, parser, mapper, handler
- **Driven Adapter** = `*_pg_repository`, ORM

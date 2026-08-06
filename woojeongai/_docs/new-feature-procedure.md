# 신규 기능 추가 절차

새 도메인·엔드포인트를 만들 때 이 순서를 지킨다.

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

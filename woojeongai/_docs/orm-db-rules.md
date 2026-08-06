# ORM · DB 규칙

## 기본 규칙

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

## Repository 번들 (Music 3NF)

- Evaluation: `sing_evaluations` → `user_vocal_recordings` → `ai_vocal_analyses` 한 트랜잭션
- Instrument/Speech: `pg_bundle_repository.save_three_part_bundle` 공통

# pgadmin-rules.local.md — 실제 로그인 정보 (로컬 전용, git 추적 안 됨)

> 이 파일은 `.gitignore`의 `*.local.md`에 걸려 커밋되지 않는다.
> 규칙·절차는 [[pgadmin-rules|pgadmin-rules.md]] 참고. 여기는 실제 값만 기록.

---

## pgAdmin 웹 UI 로그인

| 항목 | 값 |
|------|-----|
| URL | http://localhost:5050 |
| Email | admin@admin.com |
| Password | devpass1234 |

## pgAdmin 안에서 등록할 Postgres 서버(pgvector)

| 항목 | 값 |
|------|-----|
| Host name/address | pgvector |
| Port | 5432 |
| Maintenance DB | woojeongai |
| Username | postgres |
| Password | devpass1234 |

---

*출처: 저장소 루트 `.env`. `.env` 값이 바뀌면 이 파일도 같이 갱신할 것.*

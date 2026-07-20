# pgadmin-rules.md — pgAdmin 로그인·접속 규칙

> 적용 범위: `docker-compose.yaml`의 `pgadmin` 서비스 (PostgreSQL 웹 UI)

---

## 1. 접속 정보

| 항목 | 값 |
|------|-----|
| URL | `http://localhost:5050` |
| 컨테이너명 | `pgadmin_container` |
| 로그인 이메일 | `admin@admin.com` (`docker-compose.yaml`에 하드코딩, `PGADMIN_DEFAULT_EMAIL`) |
| 로그인 비밀번호 | 루트 `.env`의 `PGADMIN_DEFAULT_PASSWORD` 값 |
| 의존 서비스 | `pgvector` (기동 순서상 `depends_on`) |

- 비밀번호는 **절대 이 문서나 코드에 평문으로 적지 않는다.** `.env`에서만 관리하고, 확인이 필요하면 `.env` 파일을 직접 열어 본다 (`.env`는 `.gitignore`에 포함되어 git 추적 대상이 아니다).
- 로그인 정보가 바뀌면 `.env`의 `PGADMIN_DEFAULT_PASSWORD`만 수정한다. `docker-compose.yaml`은 수정하지 않는다.

---

## 2. 최초 로그인 후 서버(DB) 등록

pgAdmin 컨테이너와 pgvector(Postgres) 컨테이너는 **별도 컨테이너**이므로, pgAdmin 로그인 후 별도로 "Server"를 등록해야 DB에 접근할 수 있다.

| 등록 항목 | 값 | 비고 |
|-----------|-----|------|
| Host name/address | `pgvector` | `localhost` 아님 — docker network 내부 서비스명 사용 |
| Port | `5432` | |
| Maintenance DB | `.env`의 `POSTGRES_DB` 값 | |
| Username | `.env`의 `POSTGRES_USER` 값 | |
| Password | `.env`의 `POSTGRES_PASSWORD` 값 | |

- Host에 `localhost`나 `127.0.0.1`을 넣으면 연결되지 않는다. pgAdmin 컨테이너 기준으로 pgvector는 docker-compose 네트워크 내부의 `pgvector`라는 서비스명으로 접근해야 한다.

---

## 3. 로그인/접속 문제 체크리스트

```bash
# 1) 컨테이너가 떠 있는지 확인
docker compose ps pgadmin pgvector

# 2) pgadmin 컨테이너 로그 확인 (인증 오류 등)
docker compose logs pgadmin --tail=50

# 3) .env에 PGADMIN_DEFAULT_PASSWORD / POSTGRES_* 값이 비어있지 않은지 확인 (값은 출력하지 말고 존재 여부만)
grep -c "^PGADMIN_DEFAULT_PASSWORD=" .env
grep -c "^POSTGRES_" .env
```

- 로그인 화면에서 비밀번호가 계속 틀렸다고 나오면, `.env` 값을 바꾼 뒤 `pgadmin_data` 볼륨에 이전 로그인 세션/설정이 남아있어 반영이 안 될 수 있다. 이 경우 볼륨을 지워야 하므로 **반드시 사용자 승인 후** 진행한다 (`docker volume rm` 등은 데이터 삭제이므로 [[docker-rules|docker-rules.md]] 승인 절차를 따른다).

---

## 4. 안티패턴 (하지 말 것)

```text
❌ pgAdmin 로그인 비밀번호를 이 문서·커밋·PR·코드 주석에 평문으로 기록
❌ docker-compose.yaml의 PGADMIN_DEFAULT_EMAIL/PASSWORD를 .env 대신 직접 하드코딩
❌ 서버 등록 시 Host를 localhost로 입력 (컨테이너 간 네트워크이므로 서비스명 사용)
❌ 로그인 문제 해결한다며 승인 없이 pgadmin_data 볼륨 삭제
```

---

*비밀번호·API 키 등 민감 정보의 실제 값은 항상 `.env`에만 두고, 문서에는 변수명만 남긴다.*

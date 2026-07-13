# Task: pgvector 컨테이너에 야구 ERD 기반 테이블 생성 (Alembic)

## 목표
Docker Compose로 띄운 `pgvector` 컨테이너(PostgreSQL + pgvector extension)에,
아래 ERD에 정의된 4개 테이블(`stadium`, `schedule`, `team`, `player`)을
Alembic 마이그레이션으로 생성한다.

## 0단계 — 반드시 먼저 실행하고 결과를 보고할 것 (임의로 넘어가지 말 것)

1. 호스트(WSL Ubuntu) 버전 확인
   ```bash
   lsb_release -a
   ```

2. `docker-compose.yaml`에 고정된 pgvector 이미지 태그 확인
   ```bash
   grep -A2 "pgvector:" docker-compose.yaml
   ```
   현재 `pgvector/pgvector:pg17`로 고정되어 있음. 확인된 Ubuntu/Postgres 버전과
   이 이미지가 호환되는지 확인하고, 불일치가 의심되면 **임의로 이미지 태그를
   바꾸지 말고** 먼저 보고할 것.

3. 기존 Alembic 설정과 기존 마이그레이션 스타일 확인
   ```bash
   cat alembic.ini
   ls alembic/versions/
   ```
   기존 마이그레이션(`20260604_0001_titanic_person_booking_tables.py`)의
   네이밍 규칙, revision 구조, 컬럼 정의 방식을 그대로 따를 것.

## ERD 스키마 정의

### stadium
| 컬럼 | 타입 | 제약 |
|---|---|---|
| stadium_id | VARCHAR(10) | PK |
| statdium_name | VARCHAR(40) | |
| hometeam_id | VARCHAR(10) | |
| seat_count | INTEGER | |
| address | VARCHAR(60) | |
| ddd | VARCHAR(10) | |
| tel | VARCHAR(10) | |

### team
| 컬럼 | 타입 | 제약 |
|---|---|---|
| team_id | VARCHAR(10) | PK |
| region_name | VARCHAR(10) | |
| team_name | VARCHAR(40) | |
| e_team_name | VARCHAR(50) | |
| nickname | VARCHAR(10) | |
| orig_yyyy | VARCHAR(10) | |
| zip_code1 | VARCHAR(10) | |
| zip_code2 | VARCHAR(10) | |
| address | VARCHAR(80) | |
| ddd | VARCHAR(10) | |
| tel | VARCHAR(10) | |
| fax | VARCHAR(10) | |
| homepage | VARCHAR(50) | |
| owner | VARCHAR(10) | |
| stadium_id | VARCHAR(10) | FK → stadium.stadium_id |

### schedule
| 컬럼 | 타입 | 제약 |
|---|---|---|
| sche_date | VARCHAR(10) | PK |
| stadium_id | VARCHAR(10) | FK → stadium.stadium_id |
| gubun | VARCHAR(10) | |
| hometeam_id | VARCHAR(10) | FK → team.team_id |
| awayteam_id | VARCHAR(10) | FK → team.team_id |
| home_score | INTEGER | |
| away_score | INTEGER | |

### player
| 컬럼 | 타입 | 제약 |
|---|---|---|
| player_id | VARCHAR(10) | PK |
| player_name | VARCHAR(20) | |
| e_player_name | VARCHAR(40) | |
| nickname | VARCHAR(30) | |
| join_yyyy | VARCHAR(10) | |
| position | VARCHAR(10) | |
| back_no | INTEGER | |
| nation | VARCHAR(20) | |
| birth_date | DATE | |
| solar | VARCHAR(10) | |
| height | INTEGER | |
| weight | INTEGER | |
| team_id | VARCHAR(10) | FK → team.team_id |

## 가정 (Assumptions) — 진행 전 사용자에게 확인/보고할 것
- `schedule.hometeam_id`, `schedule.awayteam_id`는 다이어그램에 명시적 연결선은
  없지만 `team.team_id`와 타입·이름이 일치해 FK로 간주함. 실제 의도와 다르면
  알려달라고 보고할 것.
- `schedule`의 PK가 `sche_date` 하나뿐이면 "하루에 한 경기만" 가능한 제약이
  됨. 실제로 하루 여러 경기를 저장해야 한다면 복합키(`sche_date`,
  `hometeam_id`, `awayteam_id`) 또는 별도 `schedule_id` 서로게이트 키가 필요할
  수 있음 — 이 부분은 진행 전에 먼저 확인 질문으로 물어볼 것.

## 실행 환경 — 모든 Alembic/DB 명령은 반드시 도커 컨테이너 내부에서 실행할 것

호스트(WSL)에 alembic이나 psql이 깔려 있더라도 **호스트에서 직접 실행하지 말 것**.
`docker-compose.yaml` 기준 서비스 구성은 다음과 같음:

| 서비스명 | 컨테이너명 | 역할 |
|---|---|---|
| `backend` | `titanic_backend_container` | Python/FastAPI + Alembic 실행 환경 |
| `pgvector` | `pgvector_container` | PostgreSQL + pgvector (실제 DB) |

Alembic 관련 명령은 전부 `backend` 컨테이너 안에서, `docker compose exec`로
실행한다. DB 접속(`psql`)은 `pgvector` 컨테이너 안에서 실행한다.

먼저 두 컨테이너가 떠 있는지 확인:
```bash
docker compose ps
```
안 떠 있으면 `docker compose up -d backend pgvector`로 먼저 올릴 것.

## 작업 순서
1. 0단계 사전 확인 3가지를 실행하고 결과를 요약 보고
2. FK 의존성에 따라 생성 순서 결정: `stadium` → `team` → `schedule`, `player`
3. `backend` 컨테이너 안에서 새 Alembic revision 생성
   ```bash
   docker compose exec backend alembic revision -m "add stadium schedule team player tables"
   ```
4. `upgrade()`에 4개 테이블 생성(`op.create_table`) 작성, `downgrade()`에
   역순 drop 작성 (파일은 볼륨 마운트되어 있으므로 호스트 편집기로 열어서
   수정해도 되지만, 실행은 항상 컨테이너 안에서 할 것)
5. `backend` 컨테이너 안에서 마이그레이션 실행
   ```bash
   docker compose exec backend alembic upgrade head
   ```
6. 검증: `pgvector` 컨테이너 안에서 `psql`로 접속해 `\dt`로 4개 테이블 생성
   확인, `\d 테이블명`으로 FK 제약조건 정상 여부 확인
   ```bash
   docker compose exec pgvector psql -U $POSTGRES_USER -d $POSTGRES_DB -c '\dt'
   ```

## 완료 기준 (Definition of Done)
- [ ] 4개 테이블이 pgvector 컨테이너 안에 실제로 생성됨
- [ ] FK 제약조건(team→stadium, schedule→stadium, schedule→team×2,
      player→team)이 정상 작동
- [ ] `alembic downgrade -1` 했을 때 깨끗하게 롤백됨
- [ ] 기존 titanic 마이그레이션과 일관된 코드 스타일 유지

## 주의사항
- Docker 이미지 태그(`pgvector/pgvector:pg17`)는 임의로 변경하지 말 것
- `.env`의 `POSTGRES_*` 값을 그대로 사용할 것 (하드코딩 금지)
- 각 단계 실행 후 결과(성공/실패, 실제 명령 출력)를 요약해서 보고할 것
- Alembic/psql 명령을 호스트(WSL)에서 직접 실행하지 말 것 — 반드시
  `docker compose exec backend ...` / `docker compose exec pgvector ...`
  형태로 컨테이너 내부에서 실행할 것

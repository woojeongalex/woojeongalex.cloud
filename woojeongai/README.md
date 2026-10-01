# woojeongai — 백엔드

IUEM 의 API 서버입니다. FastAPI · Python 3.13 · PostgreSQL · Redis · S3.
전체 소개는 [저장소 루트 README](../README.md) 를 보세요.

## 띄우기

```bash
docker compose -f ../docker-compose.yaml -f ../docker-compose.local.yml up -d pgvector backend
```

`http://localhost:8000` · 문서 `/docs`.
이 폴더를 바인드 마운트하므로 코드를 고치면 uvicorn 이 바로 다시 읽습니다.

## 작업 후

```bash
~/.venvs/lint/bin/ruff check . --fix
~/.venvs/lint/bin/ruff format <이번에 고친 파일만>
```

`ruff` 는 PATH 에 없습니다. **`ruff format .` 을 전체에 돌리지 마세요** — 저장소가 포맷돼
있지 않아 무관한 파일 100여 개가 같이 바뀝니다.

## 앱

| 앱 | 역할 | 경로 |
|:--|:--|:--|
| `music_challenge` | **핵심** — 노래방·리듬 게임·악보·랭킹 | `/music_challenge/*` |
| `music` | 보컬·악기·스피치 평가 (실험실용) | `/api/music/*` |
| `friday13th` | 인증 — 가입·로그인·소셜·토큰 | `/api/auth/*` |
| `ocr` | 사진 → S3 적재 + Tesseract 글자 인식 | `/ocr/upload` |
| `auth` | RBAC 역할 검사 | (라우터 없음) |

## 계층

포트와 어댑터. **안쪽은 바깥쪽을 모릅니다.**

```
adapter/inbound/api/   HTTP 가 들어오는 곳 (라우터·스키마·매퍼)
app/ports/input/       유스케이스 인터페이스
app/use_cases/         흐름 조립
app/ports/output/      바깥에 요구하는 인터페이스
adapter/outbound/      실제 구현 (PG · S3 · librosa · ffmpeg)
domain/                순수 규칙 — 아무것도 import 하지 않는다
dependencies/          조립 (Director)
```

`domain/` 은 전부 **DB 도 서버도 없이 값만 넣어 검증할 수 있는 순수 함수**입니다.

| 파일 | 하는 일 |
|:--|:--|
| `karaoke_scoring.py` | 정답 음표 대비 음정·박자 채점 |
| `vocal_traits.py` | 발성 진단 8종 |
| `vocal_coaching.py` | 잰 값에서 조언 한 줄 |
| `next_song.py` | 약점에 맞는 다음 곡 고르기 |
| `rhythm_pattern.py` · `rhythm_scoring.py` | 리듬 게임 채보·판정 |

이 경계가 값을 한 적이 있습니다 — 조언을 LLM 에서 규칙으로 바꿀 때 **어댑터 파일 하나와
조립 한 줄**만 바뀌었습니다. 유스케이스와 도메인은 건드리지 않았습니다.

## 자세한 규칙

| 작업 | 문서 |
|:--|:--|
| 새 앱·기능 추가 | [`_docs/new-feature-procedure.md`](_docs/new-feature-procedure.md) |
| 아키텍처 | [`_docs/arch-clean-hexagonal.md`](_docs/arch-clean-hexagonal.md) |
| ORM·마이그레이션 | [`_docs/orm-db-rules.md`](_docs/orm-db-rules.md) |
| Docker·배포 | [`_docs/docker-rules.md`](_docs/docker-rules.md) |
| 곡을 노래방 챌린지로 준비 | [`_docs/song-prep-pipeline.md`](_docs/song-prep-pipeline.md) |
| 리듬 게임 채보·판정 | [`_docs/rhythm-game.md`](_docs/rhythm-game.md) |
| 작업 방식(하네스) | [`_docs/harness-engineering.md`](_docs/harness-engineering.md) |

## 이미지를 고칠 때 — 레이어 순서가 디스크를 좌우합니다

`RUN` 줄을 하나라도 고치면 **그 뒤 모든 레이어가 다시 만들어집니다.**
apt 줄에 패키지 하나를 더한 것만으로 pip 레이어(6.5GB)까지 새로 받게 되고,
실제로 운영 서버에서 디스크가 100% 차서 빌드가 죽은 적이 있습니다.

**새 시스템 패키지는 `pip install` 뒤에 별도 `RUN` 으로 넣습니다.** 그러면 100MB 남짓만
더 얹고, 빌드가 10분에서 1분 안쪽으로 줄어듭니다.

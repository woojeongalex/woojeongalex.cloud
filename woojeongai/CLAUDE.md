# CLAUDE.md — woojeongai 백엔드

세부 내용은 `_docs/` 안에 있다. 지금 하는 작업에 맞는 파일을 읽어라.

---

## 작업 유형별 읽을 파일

| 지금 하는 작업 | 읽을 파일 |
|----------------|-----------|
| 새 앱·기능 추가 | [`_docs/new-feature-procedure.md`](_docs/new-feature-procedure.md) → [`_docs/arch-clean-hexagonal.md`](_docs/arch-clean-hexagonal.md) |
| 아키텍처·폴더 구조 파악 | [`_docs/arch-clean-hexagonal.md`](_docs/arch-clean-hexagonal.md) + [`_docs/arch-layout-and-stack.md`](_docs/arch-layout-and-stack.md) |
| SOLID·의존성 주입 규칙 | [`_docs/arch-solid-and-director.md`](_docs/arch-solid-and-director.md) |
| FastAPI 라우터·패턴 작성 | [`_docs/fastapi-patterns.md`](_docs/fastapi-patterns.md) |
| ORM·DB·마이그레이션 | [`_docs/orm-db-rules.md`](_docs/orm-db-rules.md) |
| 기존 앱 현황 파악 | [`_docs/apps-status.md`](_docs/apps-status.md) |
| 코드 리뷰·PR 전 점검 | [`_docs/checklist-and-antipatterns.md`](_docs/checklist-and-antipatterns.md) |
| async/def 선택 고민 | [`_docs/async-def-guide.md`](_docs/async-def-guide.md) |
| 로깅·코딩 스타일 | [`_docs/coding-and-logging-rules.md`](_docs/coding-and-logging-rules.md) |
| Docker·배포 | [`_docs/docker-rules.md`](_docs/docker-rules.md) |
| Suno 곡을 노래방 챌린지로 준비 | [`_docs/song-prep-pipeline.md`](_docs/song-prep-pipeline.md) |
| 리듬 게임(떨어지는 노트) 채보·판정 | [`_docs/rhythm-game.md`](_docs/rhythm-game.md) |

---

## 우선순위 (충돌 시)

사용자 지시 > `vault/` > `_docs/` > 본 파일 > `../CLAUDE.md`

---

## 하네스 (작업 후 필수)

```bash
cd woojeongai
~/.venvs/lint/bin/ruff check . --fix
~/.venvs/lint/bin/ruff format <이번에 고친 파일만>
```

> **ruff 는 PATH 에 없다.** `~/.venvs/lint/bin/` 을 쓴다.
>
> **`ruff format .` 을 전체에 돌리지 말 것.** 저장소가 포맷돼 있지 않아 무관한 108개 파일이
> 재포맷된다. 이번에 고친 파일만 지정한다.
>
> **mypy 전체 실행은 멈춘다** — `alembic`/`apps` 중복 모듈 오류다. 파일을 지정해 돌린다.

# CLAUDE.md — 모노레포 인수인계 (루트)

> 모노레포 루트 → `CLAUDE.md (woojeongalex.cloud 루트)`


이 저장소는 **woojeongai(FastAPI 백엔드)** 와 **alexview(Next.js 프론트엔드)** 로 구성된 모노레포다.  
클로드(또는 Cursor 에이전트)가 바로 이어받을 수 있도록 전역 규칙과 링크를 한곳에 모았다.

**트레이드오프:** 속도보다 신중함. 사소한 작업은 상황에 맞게 판단한다.

---

## 문서 구조 (읽는 순서)

| 순서 | 문서 | 역할 |
|------|------|------|
| 1 | **본 파일** `CLAUDE.md` | 전역 원칙·행동 하네스·링크 인덱스 |
| 2 | `woojeongai/CLAUDE.md` | 백엔드 — FastAPI·클린 아키텍처·앱별 현황·ORM·체크리스트 |
| 3 | `AGENTS.md` | 행동 하네스 본문 — 가정 명시·범위 준수·검증 후 완료 |

**우선순위 (충돌 시):** 사용자 지시 > 각 앱 `CLAUDE.md` > 본 파일 > `AGENTS.md` > `.cursor/rules/*.mdc` > `.cursorrules`

---

## 저장소 레이아웃

```
woojeongalex.cloud/
  woojeongai/          # FastAPI 백엔드  →  woojeongai/CLAUDE.md
    main.py            # include_router · init_db
    apps/
      friday13th/      # 인증 (signup/login)
      music/           # 보컬·MR·악기·스피치·비디오
      titanic/         # 레퍼런스 앱  →  titanic/_docs/CLAUDE.md
    core/
      database.py      # get_db · init_db · AsyncSession
    logging_setup.py
  alexview/            # Next.js 프론트엔드  →  alexview/CLAUDE.md
```

---

## 1. 행동 하네스 요약

코딩 **전에** 반드시 지킬 것:

### Think Before Coding
- 가정을 말로 밝힌다. 모호하면 질문 후 구현.
- 해석이 여러 개면 임의 선택하지 말고 대안을 제시한다.
- 더 단순한 해법이 있으면 제안한다.

### Simplicity First
- 요청 범위 밖 기능·추상화·설정 금지.
- 일회용 추상화, 불가능한 경로 방어 코드 금지.

### Surgical Changes
- 요청과 무관한 리팩터·포맷 정리 금지. diff는 요청과 직결.
- 본인 변경으로 불필요해진 import·변수·함수만 제거.

### Goal-Driven Execution
- 검증 가능한 성공 기준 후 구현 (`import main`, API 호출, 테스트 출력).

**금지:** `.env`·비밀 커밋, 사용자 요청 없는 `git commit`/`push`/`git config` 변경.

---

## 2. 전역 아키텍처 원칙

### 아키텍처 패턴 (Non-Negotiable)
- **Hexagonal Architecture** (Ports & Adapters)
- **Clean Architecture** (의존성은 안쪽으로만 — 도메인 계층은 프레임워크 무관)
- **Domain-Driven Design** (Entities, Value Objects, Aggregates, Repositories, Domain Services)
- 세 패턴은 항상 공존·보완한다.

### SOLID 원칙
- **S** — Single Responsibility: 클래스·모듈의 변경 이유는 하나.
- **O** — Open/Closed: 확장에 열려 있고, 수정에 닫혀 있다.
- **L** — Liskov Substitution: 구현체는 Port로 교체 가능해야 한다.
- **I** — Interface Segregation: 사용하지 않는 메서드에 의존 금지.
- **D** — Dependency Inversion: 구현이 아닌 추상에 의존.

### 모듈 경로 규칙 (`woojeongai` 내부)
- `woojeongai` 접두사와 `apps` 세그먼트는 **내부 import에서 생략**.
- ✅ `from domain.wiki.entity import WikiPage`
- ❌ `from woojeongai.apps.domain.wiki.entity import WikiPage`
- 공용 core: `woojeong.core.*` 접두사 사용.
- ✅ `from woojeong.core.ports.repository import BaseRepository`
- ❌ `from core.repository import BaseRepository`

---

## 3. 언어 규칙

- 사용자가 한국어로 말하면 **한국어**로 답한다.
- 코드 주석은 **영어**로 작성한다.
- 일본어 사용 금지.
- 코드·식별자·로그 문구는 원문 유지.

---

*세부 구현 규칙은 각 앱 CLAUDE.md를 참조한다.*

---


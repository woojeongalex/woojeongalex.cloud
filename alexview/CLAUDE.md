# CLAUDE.md — alexview 프론트엔드

세부 내용은 `_docs/` 안에 있다. 지금 하는 작업에 맞는 파일을 읽어라.

---

## 작업 유형별 읽을 파일

| 지금 하는 작업 | 읽을 파일 |
|----------------|-----------|
| 처음 합류 · 전체 파악 | [`_docs/arch-layout-and-stack.md`](_docs/arch-layout-and-stack.md) |
| 컴포넌트 작성 · Server/Client 판단 | [`_docs/component-rules.md`](_docs/component-rules.md) |
| API 호출 · lib/ 연동 | [`_docs/api-rules.md`](_docs/api-rules.md) |
| 폼·상태 관리 · 에러 처리 | [`_docs/state-and-form-rules.md`](_docs/state-and-form-rules.md) |
| PR 전 점검 · 코드 리뷰 | [`_docs/checklist-and-antipatterns.md`](_docs/checklist-and-antipatterns.md) |
| 다크 모드 작업 | [`_docs/darkmode-sepc.md`](_docs/darkmode-sepc.md) |
| 디자인 토큰 · 브랜드 | [`DESIGN.md`](DESIGN.md) |
| 코딩 스타일 기준 | [`_docs/coding-rules.md`](_docs/coding-rules.md) |
| Claude의 작업 원칙 (모호한 요청) | [`_docs/behavior-principles.md`](_docs/behavior-principles.md) |
| React 코딩 규칙 | [`REACT_RULES.md`](REACT_RULES.md) |

---

## 우선순위 (충돌 시)

사용자 지시 > `_docs/` > 본 파일 > `../CLAUDE.md`

---

## 하네스 (작업 후 필수)

```bash
cd alexview
pnpm type-check
```

> 린터·포매터는 아직 붙이지 않았다. `tsc --noEmit` 하나가 전부다.
> 전에는 `pnpm lint:fix` · `pnpm format` 이 적혀 있었는데 **둘 다 정의된 적이 없다.**

# CLAUDE.md — 프론트엔드 행동 하네스 (alexview)

> 모노레포 루트 → `CLAUDE.md (woojeongalex.cloud 루트)`
> 프론트엔드 인수인계 정본 → `alexview/CLAUDE.md`
> React 코딩 규칙 → `alexview/REACT_RULES.md`

---

## 역할

이 파일은 **프론트엔드(alexview) 작업 시 행동 원칙**을 정의한다.
기술 상세(컴포넌트 규칙·API 연동·폼 패턴)는 `alexview/CLAUDE.md` 참조.
React 폼·상태 규칙은 `REACT_RULES.md` 참조.

---

## 1. Think Before Coding

- 가정을 말로 밝힌다. 모호하면 질문 후 구현.
- 해석이 여러 개면 임의 선택하지 말고 대안을 제시한다.
- 더 단순한 해법이 있으면 먼저 제안한다.

---

## 2. Simplicity First

- 요청 범위 밖 기능·추상화·훅 추가 금지.
- 일회용 추상화, 불가능한 경로 방어 코드 금지.
- 컴포넌트 분리는 재사용 근거가 있을 때만.

---

## 3. Surgical Changes

- 요청과 무관한 리팩터·포맷 정리 금지. diff는 요청과 직결.
- 본인 변경으로 불필요해진 import·변수·컴포넌트만 제거.
- 파일 하나 수정 지시 시 다른 파일 임의 수정 금지.

---

## 4. Goal-Driven Execution

- 검증 가능한 성공 기준 후 구현 (`pnpm dev` 기동 → 브라우저 확인).
- UI 변경은 골든 패스 + 엣지케이스 직접 확인 후 완료 선언.
- 타입 오류 없이 `tsc --noEmit` 통과가 최소 기준.

---

## 5. 프론트엔드 전역 원칙 (Non-Negotiable)

| 원칙 | 내용 |
|------|------|
| Server Component 기본 | `"use client"` 는 클라이언트 상태·이벤트가 필요할 때만 |
| API 추상화 | 컴포넌트에서 `fetch` 직접 호출 금지 — `lib/` 경유 |
| 폼 상태 | 필드별 `useState` 금지 — FormData 또는 React Hook Form |
| 에러 표시 | API 원문 노출 금지 — `lib/user-facing-error.ts` 필터 경유 |
| 타입 안전 | Props `interface` 명시, `any` 금지 |

---

## 6. 금지 사항

- `.env.local` 커밋 금지
- 사용자 요청 없는 `git commit` / `push` 금지
- `process.env.*` UI 날것 노출 금지
- `console.log` 디버그 커밋 금지

---

*세부 구현 규칙은 `alexview/CLAUDE.md` 와 `REACT_RULES.md` 를 참조한다.*

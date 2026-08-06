# 컴포넌트 규칙 & 전역 원칙

## 전역 원칙 (Non-Negotiable)

| 원칙 | 내용 |
|------|------|
| Server Component 기본 | `"use client"` 는 클라이언트 상태·이벤트가 필요할 때만 |
| API 추상화 | 컴포넌트에서 `fetch` 직접 호출 금지 — `lib/` 경유 |
| 폼 상태 | 필드별 `useState` 금지 — FormData 또는 React Hook Form |
| 에러 표시 | API 원문 노출 금지 — `lib/user-facing-error.ts` 필터 경유 |
| 타입 안전 | Props `interface` 명시, `any` 금지 |

## 컴포넌트 규칙

- **Server Component 기본**, 클라이언트 상태가 필요할 때만 `"use client"`.
- 페이지 컴포넌트는 데이터 패칭·라우팅만, UI 렌더링은 하위 컴포넌트에 위임.
- Props 타입은 `interface`로 명시, `any` 금지.
- Radix UI + Shadcn 기반 `components/ui/` 컴포넌트를 우선 사용.

---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

## TypeScript 규칙 (alexview 패턴 기준)

- `tsconfig.json`의 `strict: true` 유지 — 완화 금지
- `any` 타입 사용 금지 (alexview 전역에 `any` 0건)
- 타입 정의는 `interface`보다 **`type` 별칭**을 우선 사용
  (예외: 앰비언트 선언 병합이 필요한 `.d.ts`, 외부 라이브러리 타입 확장처럼 `interface`가 불가피한 경우만 허용)
- 컴포넌트 Props는 `{ComponentName}Props` type으로 선언하고, 컴포넌트 함수 인자에서 구조분해
  ```ts
  type PageBackButtonProps = {
    href?: string
    label?: string
  }

  export function PageBackButton({ href = "/", label = "뒤로가기" }: PageBackButtonProps) {
    ...
  }
  ```
- 컴포넌트는 `export function ComponentName()` 선언식 사용 (화살표 함수 `const X = () =>` 대신)
- import는 `@/*` 경로 별칭 사용 (`@/lib/...`, `@/hooks/...`, `@/components/...`), 상대경로(`../../`) 지양
- 문자열은 큰따옴표(`"`) 사용, 세미콜론 미사용 (ASI 스타일)
- API 응답/폼 데이터 등 순수 데이터 타입은 `type`으로 선언하고 필요한 필드는 옵셔널(`?`)로 명시
  (예: `lib/auth-types.ts`의 `LoginResponse`, `SignupFormFields` 참고)
- 훅은 `use-{기능}.ts`로 파일을 분리하고 `useCallback`/`useState` 등으로 상태와 액션을 명시적으로 반환

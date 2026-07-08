# React 코딩 규칙 (IUEM)

> 프론트엔드 허브 → [[alexview/CLAUDE|alexview/CLAUDE.md]]

**진입:** 루트 `.cursorrules` → `docs/DevOPs/README.md` → 본 문서  
**Cursor 주입:** `.cursor/rules/react-form-state.mdc` (`frontend/**/*.tsx`)  
**충돌 시 본 문서( docs ) 우선.**

---

## 원칙

1. **필드마다 `useState` 금지**
2. **제출 값** — `FormData` + `name` + `Object.fromEntries` 우선
3. **실시간 UI만** 별도 state/훅 (loading, error, 중복 확인 등)
4. 제어 입력이 여러 개면 **`useState` 객체 하나**

---

## FormData (권장)

```tsx
const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault()
  const formData = new FormData(e.currentTarget)
  const formProps = Object.fromEntries(formData.entries())
}
```

---

## 상태 객체 압축

```tsx
const [form, setForm] = useState<SignupFormFields>(EMPTY_SIGNUP)
const updateField = (key: keyof SignupFormFields) => (value: string) => {
  setForm((prev) => ({ ...prev, [key]: value }))
}
```

UI 전용: `useAsyncAction`, `useAvailabilityCheck`

---

## 사용자 메시지 (에러·알림)

API 원문·스택·URL·환경 변수명을 화면에 노출하지 않는다.

| 규칙 | 설명 |
|------|------|
| `UserFacingError` / `UI_ERRORS` | 허용된 문구만 throw·표시 |
| `apiErrorOrFallback` / `parseFastApiDetail` | FastAPI `detail`·`error` 필터링 |
| `useAsyncAction` | `e.message`를 그대로 UI에 넣지 않음 |
| `role="status"` | 폼·인라인 오류 (라이브 리전은 `alert` 대신 status) |

**금지:** `alert()`로 응답 JSON 표시, `error.message`·`data.error` 원문 그대로 표시, `GEMINI_API_KEY`·`API_BASE`·`localhost` 안내

참고: `frontend/lib/user-facing-error.ts`, `frontend/hooks/use-async-action.ts`

---

## 금지

- 필드마다 `useState` 나열
- FormData로 충분한데 전 필드 controlled + state 난립
- API·네트워크 오류 원문을 사용자 알림에 그대로 노출

---

## 참고

- `frontend/hooks/use-async-action.ts`
- `frontend/hooks/use-availability-check.ts`
- `frontend/app/auth/signup-form.tsx`, `login-form.tsx`
- `frontend/lib/auth-types.ts`
- `frontend/lib/user-facing-error.ts`

관련: `docs/DevOPs/Backend/BACKEND_RULES.md`, `.cursor/rules/coding-standards.mdc`

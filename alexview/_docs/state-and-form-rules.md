# 상태·폼 관리 규칙

## 폼 상태 — useState per field 금지

```tsx
// ❌ 필드마다 useState 남발
const [id, setId] = useState("")
const [pw, setPw] = useState("")

// ✅ FormData + Object.fromEntries (단순 폼)
async function handleSubmit(e: FormEvent<HTMLFormElement>) {
  e.preventDefault()
  const data = Object.fromEntries(new FormData(e.currentTarget))
  await login(data)
}

// ✅ React Hook Form (복잡한 폼 · 유효성 검사)
const { register, handleSubmit, formState } = useForm<LoginForm>({
  resolver: zodResolver(loginSchema),
})
```

## 허용되는 UI 상태

- `loading` (boolean)
- `error` (string | null)
- 가용성 체크 결과 (ID·닉네임 중복)
- 단일 압축 상태 객체 (`{ loading, error, result }`)

## 커스텀 훅 활용

```tsx
// 비동기 액션 래퍼 — loading·error 자동 관리
const { loading, error, run } = useAsyncAction(loginApi)

// 중복 체크 훅
const { available, checking, check } = useAvailabilityCheck("id")
```

## 에러 표시 규칙

- 사용자에게 API 원문 에러 메시지(`error.message`) 날것 노출 금지.
- `lib/user-facing-error.ts`의 필터링 함수 경유, 안전한 메시지만 렌더링.
- `lib/auth-messages.ts` 등 메시지 상수 파일에서 관리.

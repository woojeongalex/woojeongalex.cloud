# 코딩·리뷰 체크리스트 & 금지 사항

## 코딩·리뷰 체크리스트

- [ ] 컴포넌트에서 `fetch` 직접 호출 없는가?
- [ ] 폼 상태가 필드별 `useState` 없이 FormData 또는 RHF로 처리되는가?
- [ ] 에러 메시지가 `user-facing-error` 필터링을 거치는가?
- [ ] 환경 변수가 `lib/` 래핑 없이 UI에 직접 노출되지 않는가?
- [ ] `"use client"` 가 실제 클라이언트 상태·이벤트가 필요한 컴포넌트에만 붙어 있는가?
- [ ] Props가 `interface`로 타입 명시되어 있는가?
- [ ] `tsc --noEmit` 통과하는가?
- [ ] diff가 사용자 요청 범위만 포함하는가?

## 금지 사항 (코드)

```tsx
// ❌ 필드 per useState 남발
const [username, setUsername] = useState("")
const [password, setPassword] = useState("")

// ❌ 컴포넌트에서 fetch 직접 호출
const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/...`)

// ❌ 원문 에러 노출
<p>{error.message}</p>

// ❌ 환경 변수 UI 날것 노출
<span>{process.env.NEXT_PUBLIC_API_URL}</span>

// ❌ 불필요한 "use client" — 서버 컴포넌트로 충분한 경우
"use client"
export default function StaticPage() { ... }
```

## 금지 사항 (운영)

- `.env.local` 커밋 금지
- 사용자 요청 없는 `git commit` / `push` 금지
- `console.log` 디버그 커밋 금지

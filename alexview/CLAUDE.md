# CLAUDE.md — 프론트엔드 (alexview)

> React 코딩 규칙 → [[REACT_RULES|alexview/REACT_RULES.md]]

**우선순위 (충돌 시):** 사용자 지시 > 본 파일 > `../CLAUDE.md`

---

## 0. 문서 읽는 순서 (프론트엔드)

| 순서 | 문서 | 역할 |
|------|------|------|
| 1 | `../CLAUDE.md` | 전역 원칙·행동 하네스 |
| 2 | **본 파일** `alexview/CLAUDE.md` | 프론트엔드 인수인계 정본 |

---

## 1. 행동 원칙

### Think Before Coding

- 가정을 말로 밝힌다. 모호하면 질문 후 구현.
- 해석이 여러 개면 임의 선택하지 말고 대안을 제시한다.
- 더 단순한 해법이 있으면 먼저 제안한다.

### Simplicity First

- 요청 범위 밖 기능·추상화·훅 추가 금지.
- 일회용 추상화, 불가능한 경로 방어 코드 금지.
- 컴포넌트 분리는 재사용 근거가 있을 때만.

### Surgical Changes

- 요청과 무관한 리팩터·포맷 정리 금지. diff는 요청과 직결.
- 본인 변경으로 불필요해진 import·변수·컴포넌트만 제거.
- 파일 하나 수정 지시 시 다른 파일 임의 수정 금지.

### Goal-Driven Execution

- 검증 가능한 성공 기준 후 구현 (`pnpm dev` 기동 → 브라우저 확인).
- UI 변경은 골든 패스 + 엣지케이스 직접 확인 후 완료 선언.
- 타입 오류 없이 `tsc --noEmit` 통과가 최소 기준.

---

## 2. 기술 스택

| 항목 | 버전 |
|------|------|
| Next.js (App Router) | 16.2.4 |
| React / React DOM | 19 |
| TypeScript | 5.7.3 |
| Tailwind CSS | 4.2.0 |
| Radix UI | 20+ primitives |
| React Hook Form | 7.54.1 |
| Zod | (hookform/resolvers) |
| recharts | 2.15.0 |
| sonner (toast) | 1.7.1 |
| next-themes (dark mode) | 0.4.6 |
| @google/generative-ai | 0.24.1 |
| pnpm | 9.15.9 |

---

## 3. 저장소 레이아웃

```
alexview/
  app/                         # Next.js App Router 페이지
    layout.tsx                 # 루트 레이아웃
    page.tsx                   # 홈
    globals.css
    auth/                      # 인증 페이지 (login, signup)
    titanic/                   # Titanic 기능 페이지
    analyze/                   # 영상·음성 분석
    instrument/                # 악기 평가
    speech/                    # 스피치 평가
    mypage/                    # 사용자 프로필
    api/                       # Next.js API Routes (백엔드 프록시)
      auth/                    # login / signup / check-id / check-nickname
      music/[...path]/         # Music API 프록시
      titanic/[...path]/       # Titanic API 프록시
      chat/ gemini/ songs/ weather/
  components/
    ui/                        # Radix UI + Shadcn/ui (button, input, dialog ...)
  lib/                         # API 클라이언트·유틸
    auth-client.ts             # 인증 API 추상화
    auth-session.ts            # 세션 관리
    titanic-api.ts
    song-mr-api.ts
    sing-evaluation-api.ts
    music-api-fetch.ts
    speech-api.ts
    instrument-api.ts
    gemini-generate.ts
    utils.ts                   # cn() 등 공통 유틸
  hooks/                       # 커스텀 React 훅
    use-async-action.ts        # 로딩·에러 상태 관리
    use-availability-check.ts  # 중복 ID/닉네임 체크
    use-mic-recording.ts       # 마이크 녹음
    use-user-session.ts        # 유저 세션
  types/                       # TypeScript 타입 정의
  public/                      # 정적 파일
```

- 로컬 실행: `cd alexview` → `pnpm dev` (포트 3000)
- 타입 검사: `pnpm tsc --noEmit`

---

## 4. 전역 원칙 (Non-Negotiable)

| 원칙 | 내용 |
|------|------|
| Server Component 기본 | `"use client"` 는 클라이언트 상태·이벤트가 필요할 때만 |
| API 추상화 | 컴포넌트에서 `fetch` 직접 호출 금지 — `lib/` 경유 |
| 폼 상태 | 필드별 `useState` 금지 — FormData 또는 React Hook Form |
| 에러 표시 | API 원문 노출 금지 — `lib/user-facing-error.ts` 필터 경유 |
| 타입 안전 | Props `interface` 명시, `any` 금지 |

---

## 5. API 연동 규칙

- 백엔드 호출은 `lib/` 아래 API 클라이언트 함수로 추상화한다.
- **컴포넌트에서 `fetch`/`axios` 직접 호출 금지** — `lib/` 경유 필수.
- Next.js API Routes(`app/api/`)는 백엔드 프록시 역할만 한다.
- 환경 변수: `NEXT_PUBLIC_API_URL` (`.env.local` — 커밋 금지).
- UI에 `process.env.*` 날것 노출 금지 — `lib/` 에서 래핑.

---

## 6. 컴포넌트 규칙

- **Server Component 기본**, 클라이언트 상태가 필요할 때만 `"use client"`.
- 페이지 컴포넌트는 데이터 패칭·라우팅만, UI 렌더링은 하위 컴포넌트에 위임.
- Props 타입은 `interface`로 명시, `any` 금지.
- Radix UI + Shadcn 기반 `components/ui/` 컴포넌트를 우선 사용.

---

## 7. 상태·폼 관리 규칙

### 7.1 폼 상태 — useState per field 금지

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

### 7.2 허용되는 UI 상태

- `loading` (boolean)
- `error` (string | null)
- 가용성 체크 결과 (ID·닉네임 중복)
- 단일 압축 상태 객체 (`{ loading, error, result }`)

### 7.3 커스텀 훅 활용

```tsx
// 비동기 액션 래퍼 — loading·error 자동 관리
const { loading, error, run } = useAsyncAction(loginApi)

// 중복 체크 훅
const { available, checking, check } = useAvailabilityCheck("id")
```

### 7.4 에러 표시 규칙

- 사용자에게 API 원문 에러 메시지(`error.message`) 날것 노출 금지.
- `lib/user-facing-error.ts`의 필터링 함수 경유, 안전한 메시지만 렌더링.
- `lib/auth-messages.ts` 등 메시지 상수 파일에서 관리.

---

## 8. 코딩 규칙

- **코드만 출력** — 설명·주석 불필요 시 생략
- **수정 범위 엄수** — 지시한 파일·부분만 수정, 임의 리팩터링 금지
- 타입 오류 없이 `tsc --noEmit` 통과
- 같은 패턴 파일 수정 시 동일 패턴의 모든 파일을 찾아 일괄 점검·적용

---

## 9. 금지 사항

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

- `.env.local` 커밋 금지
- 사용자 요청 없는 `git commit` / `push` 금지
- `console.log` 디버그 커밋 금지

---

## 10. 코딩·리뷰 체크리스트

- [ ] 컴포넌트에서 `fetch` 직접 호출 없는가?
- [ ] 폼 상태가 필드별 `useState` 없이 FormData 또는 RHF로 처리되는가?
- [ ] 에러 메시지가 `user-facing-error` 필터링을 거치는가?
- [ ] 환경 변수가 `lib/` 래핑 없이 UI에 직접 노출되지 않는가?
- [ ] `"use client"` 가 실제 클라이언트 상태·이벤트가 필요한 컴포넌트에만 붙어 있는가?
- [ ] Props가 `interface`로 타입 명시되어 있는가?
- [ ] `tsc --noEmit` 통과하는가?
- [ ] diff가 사용자 요청 범위만 포함하는가?

---

*세부 규칙 추가 시 본 파일을 업데이트한다.*



## 11. 다크 모드

[darkmode-sepc.md](./_docs/darkmode-sepc.md)
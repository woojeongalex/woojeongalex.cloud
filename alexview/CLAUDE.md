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
      chat/ gemini/ songs/
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

---

## 12. 디자인 시스템 (Design Tokens + Brand Philosophy)

> AI 코딩 에이전트가 UI 작업 시 따라야 하는 브랜드 스펙.
> 디자인 토큰(어떻게 생겼나) + 브랜드 철학(어떻게 행동하나).

### 12.1 Color Palette

#### Semantic Tokens (oklch, CSS Variables)

시스템 전체가 **모노크롬 뉴트럴**(chroma=0)로 구성되어 있다.
유채색은 브랜드 액센트(sky-600 블루)에만 사용한다.

| 토큰 | Light | Dark | 용도 |
|------|-------|------|------|
| `--background` | `#FFFFFF` | `#171717` | 페이지 배경 |
| `--foreground` | `#171717` | `#FAFAFA` | 기본 텍스트 |
| `--primary` | `#171717` | `#FAFAFA` | CTA 버튼, 주요 액션 |
| `--primary-foreground` | `#FAFAFA` | `#171717` | CTA 위 텍스트 |
| `--secondary` | `#F5F5F5` | `#383838` | 보조 배경 |
| `--muted` | `#F5F5F5` | `#383838` | 비활성 배경 |
| `--muted-foreground` | `#737373` | `#A3A3A3` | 보조 텍스트, 힌트 |
| `--border` | `#E5E5E5` | `#383838` | 테두리, 구분선 |
| `--destructive` | red-600 계열 | red-400 계열 | 에러, 위험 동작 |

#### Brand Accent (유일한 유채색)

| 이름 | Hex | 용도 |
|------|-----|------|
| Sky-600 | `#0284C7` | 브랜드 그라데이션 시작, 로고 아이콘 |
| Sky-500 | `#0EA5E9` | 브랜드 그라데이션 중간 |
| Cyan-600 | `#0891B2` | 브랜드 그라데이션 끝 |

브랜드 블루는 **히어로 타이틀 그라데이션**, **로그인 아이콘**, **커리큘럼 하이라이트 셀**에만 사용한다.
일반 UI 요소(버튼, 카드, 입력 필드)에는 뉴트럴만 쓴다.

#### 확장 스케일 (Tailwind zinc 기준)

| 단계 | Hex | 역할 |
|------|-----|------|
| zinc-50 | `#FAFAFA` | hover 배경, 입력 필드 배경 |
| zinc-100 | `#F4F4F5` | 아이콘 컨테이너, 드롭존 |
| zinc-200 | `#E4E4E7` | 테두리, 구분선 |
| zinc-300 | `#D4D4D8` | 입력 테두리, 보조 테두리 |
| zinc-400 | `#A1A1AA` | 보조 텍스트, 아이콘 |
| zinc-500 | `#71717A` | 플레이스홀더, 3차 텍스트 |
| zinc-800 | `#27272A` | 다크 버튼, 메뉴 hover |
| zinc-900 | `#18181B` | 1차 버튼, CTA |
| zinc-950 | `#09090B` | 배너 배경, 가장 어두운 면 |

#### 서드파티 브랜드 색상 (소셜 로그인 전용)

| 브랜드 | 배경 | 텍스트 |
|--------|------|--------|
| 카카오 | `#FEE500` | `#191919` |
| 네이버 | `#03C75A` | `#FFFFFF` |
| 구글 | `#FFFFFF` | `#171717` |

이 색상은 해당 서비스의 공식 가이드라인을 따르며, 브랜드 팔레트와 무관하다.

### 12.2 Typography

#### 폰트 패밀리

| Sans | Mono |
|------|------|
| Geist | Geist Mono |

> **한국어 폰트 미지정 상태.** `lang="ko"` 설정은 되어 있으나 Pretendard 등 전용 서체는
> 로드하지 않고 OS 기본 한국어 폰트에 의존한다.

#### 타입 스케일

| 용도 | Tailwind | 크기 | Weight |
|------|----------|------|--------|
| 히어로 제목 | `text-6xl` | 60px | 800 |
| 섹션 제목 | `text-3xl` | 30px | 700 |
| 카드 제목 | `text-2xl` | 24px | 700 |
| 소제목 | `text-xl` | 20px | 600 |
| 본문 | `text-sm` | 14px | 400 |
| 라벨 | `text-xs` | 12px | 500 |
| 캡션 | `text-[10px]` | 10px | 500 |

#### Letter Spacing

| 용도 | 값 |
|------|-----|
| 제목 (타이트) | `-0.5px` ~ `-0.2px` |
| 본문 | 기본값 |
| 섹션 라벨 (와이드) | `1.5px` ~ `3.0px` |

### 12.3 Rounded

| 토큰 | 값 | 용도 |
|------|----|------|
| `--radius` (base) | 10px | 기준값 |
| `radius-sm` | 6px | 메뉴 항목, 캘린더 셀 |
| `radius-md` | 8px | 버튼, 입력 필드, 탭, 배지 |
| `radius-lg` | 10px | 카드, 다이얼로그, 드롭다운 |
| `radius-xl` | 14px | 인증 입력, CTA 버튼 |
| `2xl` | 16px | 배너, 드롭존, 인증 패널 |
| `3xl` | 24px | 대형 배너 |
| `[2rem]` | 32px | CTA 섹션, 인증 브랜딩 패널 |
| `full` | 9999px | 태그 필, 아바타, 전송 버튼 |

### 12.4 Shadows

| 단계 | 용도 |
|------|------|
| `shadow-xs` | 입력 필드, 체크박스, 토글 |
| `shadow-sm` | 카드, 탭 |
| `shadow-md` | 드롭다운, 팝오버 |
| `shadow-lg` | 다이얼로그, 시트 |
| 없음 | 대부분의 카드, 배너 (테두리로 구분) |

그림자보다 **테두리(border)**로 요소를 구분하는 것이 기본 원칙이다.
플로팅 요소(드롭다운, 다이얼로그)에만 그림자를 쓴다.

### 12.5 Spacing

4px 배수 체계를 따른다.

| 단계 | 값 | 주 용도 |
|------|----|---------|
| 1 | 4px | 인라인 간격 |
| 2 | 8px | 요소 간 기본 간격 |
| 3 | 12px | 입력 내부 패딩 |
| 4 | 16px | 카드 내부, 섹션 내 그룹 간격 |
| 6 | 24px | 카드 주요 패딩, 컬럼 간격 |
| 8 | 32px | 섹션 간 수직 패딩 (모바일) |
| 12 | 48px | 섹션 간 수직 패딩 (데스크톱) |
| 16 | 64px | 히어로 섹션 수직 패딩 |

컨테이너 최대 너비: `max-w-6xl` (1152px).

### 12.6 Motion

| 속성 | 기본값 | 규칙 |
|------|--------|------|
| Duration | 200ms | 대부분의 전환 |
| Easing | ease-in-out | 시트, 슬라이드 |
| 전환 대상 | `transition-colors` | 버튼, 링크, 입력 필드 |
| 긴 전환 | 300ms–500ms | 시트 열기/닫기, 캐러셀 페이드 |

허용: fade-in/out, slide-in/out, zoom-in-95/out-95, accordion, pulse, spin.
금지: 바운스, 스프링, 3D 회전, 파티클, 패럴랙스, 스크롤 스냅.

120ms–200ms ease-out 기본. 튀는 효과 금지.

### 12.7 UI Framework

| 프레임워크 | 스타일 |
|-----------|--------|
| shadcn/ui | **new-york** 변형 |
| Tailwind CSS 4 | 유틸리티 우선 |
| Radix UI | 헤드리스 접근성 프리미티브 |

shadcn/ui 컴포넌트는 시맨틱 토큰(`bg-background`, `text-foreground`, `border-border`)을
사용하고, 하드코딩 색상은 피한다.

### 12.8 Voice

해요체. 금지어: '고객님', '~하옵니다', '~되겠습니다'.

```
O: "분석이 완료됐어요"
O: "파일을 올려주세요"
X: "고객님, 분석이 완료되었습니다"
X: "파일을 업로드해 주시기 바랍니다"
```

에러 메시지도 같은 톤. 기술 용어는 그대로 쓰되 문장은 짧게.

### 12.9 Narrative

**"실무로 배우는 AI 서비스 개발"**

AX Academy는 IBM x Red Hat이 함께하는 K-Digital Training 프로그램이다.
UI에서는 "교육" 대신 **"프로젝트"**, **"실습"** 을 강조하고,
추상적 설명보다 **구체적 기술명**을 노출한다 (FastAPI, RAG, ...).
과장 없이 사실 기반으로 서술.

### 12.10 Principles

충돌 시 우선순위:

1. **명확성** > 화려함 — 모노크롬 뉴트럴이 기본, 유채색은 브랜드 블루만
2. **기능** > 장식 — 그림자보다 테두리, 애니메이션은 피드백 목적만
3. **일관성** > 독창성 — shadcn/ui 기본 패턴을 따르고 커스텀은 최소화
4. **접근성** > 심미성 — 명암 대비 4.5:1 이상, 키보드 네비게이션 보장

### 12.11 Personas

| 페르소나 | 설명 |
|----------|------|
| 1차 | 20–30대, 개발 전환자 또는 주니어 개발자. AI 서비스 개발을 처음 배운다. |
| 2차 | 교육 운영자(강사). 수강생 진도와 결과물을 관리한다. |

- 전문 용어는 써도 되지만, 첫 등장 시 맥락이 이해 가능해야 한다
- 모바일 우선 — 수강생은 통학 중 폰으로 접근한다
- 로딩이 느리면 이탈한다 — 스켈레톤 즉시 표시

### 12.12 States

| 상태 | 처리 원칙 |
|------|-----------|
| Empty | 항상 다음 행동을 제안한다. "아직 업로드된 파일이 없어요. 이미지를 올려보세요." |
| Loading | 스켈레톤(pulse) 즉시 표시. 2초 이상 걸리면 진행 상태 텍스트 추가. |
| Error | 원인 + 해결 방법을 함께 표시. 재시도 버튼 제공. |
| Success | 토스트로 짧게 알림. 자동 사라짐 4초. |
| Disabled | opacity 50%, 커서 not-allowed. 왜 비활성인지 툴팁으로 설명. |
# DESIGN.md — 디자인 시스템 (Design Tokens + Brand Philosophy)

> AI 코딩 에이전트가 UI 작업 시 따라야 하는 브랜드 스펙.
> 디자인 토큰(어떻게 생겼나) + 브랜드 철학(어떻게 행동하나).
>
> **2026-09-22 신스웨이브 테마로 바꿨다.** 사용자가 시안 A3(네온 석양 + 격자)을 골랐다.
> 사이트 전체가 어두운 테마 하나다(라이트 모드 없음, `ThemeProvider forcedTheme="dark"`).

---

## 1. Color Palette

### Semantic Tokens (`app/globals.css`, `:root` = `.dark`)

| 토큰 | 값 | 용도 |
|------|----|------|
| `--background` | `#0D0619` | 페이지 배경(보랏빛 밤하늘) |
| `--foreground` | `#F1E6FF` | 기본 텍스트 |
| `--card` | `#160A2B` | 카드·패널 |
| `--popover` | `#1A0B33` | 드롭다운·팝오버 |
| `--primary` | `#FF2E97` | 브랜드 네온 핑크 — 주요 버튼, 선택 상태, 판정선 |
| `--secondary` / `--muted` | `#22103F` / `#1D0D38` | 보조 배경 |
| `--muted-foreground` | `#A995CC` | 보조 텍스트 |
| `--accent` | `#2A1450` | 호버 배경 |
| `--border` / `--input` | `#3B1D66` | 테두리 |
| `--destructive` | `#FF4D6D` | 에러 |
| `--chart-1..5` | 핑크·시안·보라·노랑·주황 | 차트 |

### 네온 강조색 (`@theme` 의 `neon-*`)

| 이름 | Hex | 용도 |
|------|-----|------|
| `neon-pink` | `#FF2E97` | 브랜드. CTA, 선택, 강조 |
| `neon-cyan` | `#2EE6FF` | 보조 버튼, 섹션 라벨, 정보, 리듬 게임 COOL |
| `neon-violet` | `#B44CFF` | 격자·장식 |
| `neon-yellow` | `#FFD23F` | 순위·경고, 석양 윗부분 |
| `neon-orange` | `#FF7A3D` | 석양 가운데 |
| `neon-green` | `#3DDC97` | 성공, 쉬움 난이도 |

### 밤하늘 단계 (`night-*`)

`night-950 #0D0619` → `900 #12072A` → `850 #160A2B` → `800 #1A0B33` → `700 #22103F` → `600 #3B1D66` → `500 #5A2D99`.
바탕 → 패널 → 테두리 순. 무대(캔버스) 배경은 `night-950`.

색은 토큰·`neon-*`·`night-*` 로만 쓴다. `zinc-*`, `sky-*`, `bg-white` 같은 하드코딩 금지.

### 서드파티 브랜드 색상 (소셜 로그인 전용)

| 브랜드 | 배경 | 텍스트 |
|--------|------|--------|
| 카카오 | `#FEE500` | `#191919` |
| 네이버 | `#03C75A` | `#FFFFFF` |
| 구글 | `#FFFFFF` | `#171717` |

이 색상은 해당 서비스의 공식 가이드라인을 따르며, 브랜드 팔레트와 무관하다.

---

## 2. Typography

| 역할 | 글꼴 | Tailwind |
|------|------|----------|
| 본문 | IBM Plex Sans KR | `font-sans` (기본) |
| 큰 한글 제목 | Black Han Sans | `font-display` |
| 영문 네온 라벨·로고·점수 | Orbitron | `font-orbitron` |
| 숫자·코드 | JetBrains Mono | `font-mono` |

`app/layout.tsx` 에서 `next/font/google` 로 불러온다. 한글 글꼴은 `preload: false`.

### 타입 스케일

| 용도 | Tailwind | 비고 |
|------|----------|------|
| 히어로 제목 | `font-display text-5xl~7xl` + `neon-text` | |
| 섹션 제목 | `font-display text-3xl~4xl text-white` | `SectionHeading` |
| 섹션 라벨 | `font-orbitron text-xs tracking-[0.25em] text-neon-cyan` | 제목 위 |
| 카드 제목 | `text-xl~2xl font-semibold` 또는 `font-display` | |
| 본문 | `text-sm~base` | 행간 넉넉히(`leading-6~8`) |

---

## 신스웨이브 전용 부품

| 이름 | 위치 | 용도 |
|------|------|------|
| `SynthBackdrop` | `components/common/synth-backdrop.tsx` | 히어로 배경 — 줄무늬 석양 + 흘러오는 격자 바닥 |
| `neon-text` / `neon-text-cyan` | globals.css | 네온 글씨 |
| `glow-card` | globals.css | 누를 수 있는 카드. 올리면 떠오르며 핑크 테두리가 빛남 |
| `glow-button` | globals.css | 주요 버튼의 네온 빛 |
| `shimmer animate-shimmer` | globals.css | 로딩 자리(`LoadingBlock`) |
| 별빛 | `body::before` | 사이트 전체 뒤 반짝이는 별 |

---

## 3. Rounded

| 토큰 | 값 | 용도 |
|------|----|------|
| `--radius` (base) | 14px | 기준값 |
| `radius-sm` | 6px | 메뉴 항목, 캘린더 셀 |
| `radius-md` | 8px | 버튼, 입력 필드, 탭, 배지 |
| `radius-lg` | 10px | 카드, 다이얼로그, 드롭다운 |
| `radius-xl` | 14px | 인증 입력, CTA 버튼 |
| `2xl` | 16px | 배너, 드롭존, 인증 패널 |
| `3xl` | 24px | 대형 배너 |
| `[2rem]` | 32px | CTA 섹션, 인증 브랜딩 패널 |
| `full` | 9999px | 태그 필, 아바타, 전송 버튼 |

---

## 4. Shadows

| 단계 | 용도 |
|------|------|
| `shadow-xs` | 입력 필드, 체크박스, 토글 |
| `shadow-sm` | 카드, 탭 |
| `shadow-md` | 드롭다운, 팝오버 |
| `shadow-lg` | 다이얼로그, 시트 |
| 없음 | 대부분의 카드, 배너 (테두리로 구분) |

요소 구분은 테두리가 기본이고, 강조할 곳(주요 버튼, 선택된 카드, 판정선)에만 네온 빛(핑크 그림자)을 쓴다.
회색 그림자 대신 `shadow-[0_0_24px_-6px_#ff2e97]` 같은 색 있는 빛을 쓴다.

---

## 5. Spacing

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

---

## 6. Motion

| 속성 | 기본값 | 규칙 |
|------|--------|------|
| Duration | 200ms | 대부분의 전환 |
| Easing | ease-in-out | 시트, 슬라이드 |
| 전환 대상 | `transition-colors` | 버튼, 링크, 입력 필드 |
| 긴 전환 | 300ms–500ms | 시트 열기/닫기, 캐러셀 페이드 |

허용: 등장(fade-in + slide-in-from-bottom, 120ms 간격으로 순서대로), 석양 빛 맥동(`animate-sun-pulse`), 격자 흐름(`animate-synth-grid`), 로고 깜빡임(`animate-neon-flicker`), 카드 떠오름(`glow-card`), 로딩 물결(`animate-shimmer`).
금지: 바운스, 스프링, 스크롤을 가로채는 효과. 반복 애니메이션은 장식에만 쓰고 글자를 움직이지 않는다.

`prefers-reduced-motion` 이면 globals.css 가 모든 애니메이션을 끈다.

---

## 7. UI Framework

| 프레임워크 | 스타일 |
|-----------|--------|
| shadcn/ui | **new-york** 변형 |
| Tailwind CSS 4 | 유틸리티 우선 |
| Radix UI | 헤드리스 접근성 프리미티브 |

shadcn/ui 컴포넌트는 시맨틱 토큰(`bg-background`, `text-foreground`, `border-border`)을
사용하고, 하드코딩 색상은 피한다.

---

## 8. Voice

해요체. 금지어: '고객님', '~하옵니다', '~되겠습니다'.

```
O: "분석이 완료됐어요"
O: "파일을 올려주세요"
X: "고객님, 분석이 완료되었습니다"
X: "파일을 업로드해 주시기 바랍니다"
```

에러 메시지도 같은 톤. 기술 용어는 그대로 쓰되 문장은 짧게.

---

## 9. Narrative

**"실무로 배우는 AI 서비스 개발"**

AX Academy는 IBM x Red Hat이 함께하는 K-Digital Training 프로그램이다.
UI에서는 "교육" 대신 **"프로젝트"**, **"실습"** 을 강조하고,
추상적 설명보다 **구체적 기술명**을 노출한다 (FastAPI, RAG, ...).
과장 없이 사실 기반으로 서술.

---

## 10. Principles

충돌 시 우선순위:

1. **명확성** > 화려함 — 밤하늘 바탕에 네온은 강조할 곳에만. 한 화면에 핑크 주 버튼은 하나
2. **기능** > 장식 — 장식 애니메이션은 히어로·배경에만, 게임 화면은 판정 피드백 위주
3. **일관성** > 독창성 — shadcn/ui 기본 패턴을 따르고 커스텀은 최소화
4. **접근성** > 심미성 — 명암 대비 4.5:1 이상, 키보드 네비게이션 보장

---

## 11. Personas

| 페르소나 | 설명 |
|----------|------|
| 1차 | 20–30대, 개발 전환자 또는 주니어 개발자. AI 서비스 개발을 처음 배운다. |
| 2차 | 교육 운영자(강사). 수강생 진도와 결과물을 관리한다. |

- 전문 용어는 써도 되지만, 첫 등장 시 맥락이 이해 가능해야 한다
- 모바일 우선 — 수강생은 통학 중 폰으로 접근한다
- 로딩이 느리면 이탈한다 — 스켈레톤 즉시 표시

---

## 12. States

| 상태 | 처리 원칙 |
|------|-----------|
| Empty | 항상 다음 행동을 제안한다. "아직 업로드된 파일이 없어요. 이미지를 올려보세요." |
| Loading | 스켈레톤(pulse) 즉시 표시. 2초 이상 걸리면 진행 상태 텍스트 추가. |
| Error | 원인 + 해결 방법을 함께 표시. 재시도 버튼 제공. |
| Success | 토스트로 짧게 알림. 자동 사라짐 4초. |
| Disabled | opacity 50%, 커서 not-allowed. 왜 비활성인지 툴팁으로 설명. |

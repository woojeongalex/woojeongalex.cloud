#music - 테마 지시어 (2026-09-22 신스웨이브 단일 테마)

## 구현 방식

- 사이트 전체가 **어두운 신스웨이브 테마 하나**다. 라이트 모드와 테마 전환 버튼은 없앴다.
- `next-themes` 의 `ThemeProvider` 는 `forcedTheme="dark"` 로 고정한다. 기존 컴포넌트의 `dark:` 변형이 늘 켜지도록 하기 위해서다.
- `app/globals.css` 에서 `:root` 와 `.dark` 가 같은 값을 갖는다.

## 파일 목록

| 파일 | 역할 |
|------|------|
| `app/layout.tsx` | 글꼴(next/font), `ThemeProvider forcedTheme="dark"` |
| `app/globals.css` | 색 토큰, `neon-*`·`night-*` 색, 애니메이션, `neon-text`·`glow-card` 등 |
| `components/common/synth-backdrop.tsx` | 석양 + 격자 히어로 배경 |
| `components/site-header.tsx` | 네온 헤더(현재 메뉴 강조) |

## 색상 규칙

하드코딩 금지. 토큰과 네온 색만 쓴다. 자세한 표는 `DESIGN.md` 1절.

| 용도 | 클래스 |
|------|--------|
| 배경 | `bg-background`, 패널 `bg-card` |
| 텍스트 | `text-foreground`, 보조 `text-muted-foreground` |
| 테두리 | `border-border` |
| 호버 배경 | `hover:bg-accent` |
| 강조 | `bg-primary`·`text-neon-pink`, 보조 `text-neon-cyan` |

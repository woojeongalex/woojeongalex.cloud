#music - 다크모드 구현 지시어

## 구현 방식

- `next-themes` 라이브러리 사용 (`ThemeProvider`, `useTheme`)
- `attribute="class"` 방식으로 `<html>` 에 `.dark` 클래스 토글
- `defaultTheme="dark"` — 앱 최초 실행 시 다크 모드 적용
- `enableSystem={false}` — OS 설정 무시, 명시적 기본값 사용

## 파일 목록

| 파일 | 역할 |
|------|------|
| `app/layout.tsx` | `ThemeProvider` 래핑, `suppressHydrationWarning` |
| `components/theme-provider.tsx` | `next-themes` 래퍼 컴포넌트 |
| `components/site-header.tsx` | `ThemeToggle` 버튼 (Sun/Moon 아이콘) |
| `styles/globals.css` | `:root` (라이트) / `.dark` (다크) CSS 변수 정의 |

## 색상 변수 규칙

하드코딩 금지. 아래 Tailwind 유틸리티 클래스를 사용한다.

| 용도 | 클래스 |
|------|--------|
| 배경 | `bg-background` |
| 텍스트 | `text-foreground` |
| 보조 텍스트 | `text-muted-foreground` |
| 테두리 | `border-border` |
| 호버 배경 | `hover:bg-accent` |

# API 연동 규칙

- 백엔드 호출은 `lib/` 아래 API 클라이언트 함수로 추상화한다.
- **컴포넌트에서 `fetch`/`axios` 직접 호출 금지** — `lib/` 경유 필수.
- Next.js API Routes(`app/api/`)는 백엔드 프록시 역할만 한다.
- 환경 변수: `NEXT_PUBLIC_API_URL` (`.env.local` — 커밋 금지).
- UI에 `process.env.*` 날것 노출 금지 — `lib/` 에서 래핑.

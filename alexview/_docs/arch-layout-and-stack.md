# 저장소 레이아웃 & 기술 스택

## 기술 스택

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

## 저장소 레이아웃

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

---
title: 시스템 구성
nav_order: 3
---

# 시스템 구성
{: .no_toc }

1. TOC
{:toc}

---

## 저장소

하나의 모노레포에 세 개의 앱이 있다.

| 폴더 | 역할 | 기술 |
|:--|:--|:--|
| `woojeongai/` | 백엔드 API | FastAPI · SQLModel · Alembic · PostgreSQL(pgvector) · Redis · librosa |
| `alexview/` | 웹 프론트엔드 | Next.js 16 (App Router) · React 19 · Tailwind 4 · shadcn/ui |
| `alexthegreat/` | 모바일 앱 | Flutter |
| `woojeongai/tools/song_prep/` | 곡 준비 도구 (관리자 PC 에서 실행) | Demucs · faster-whisper · Docker |

백엔드는 앱마다 클린 아키텍처로 나눈다 — `domain`(엔티티·값 객체·규칙) → `app`(유스케이스·포트) → `adapter`(API·DB·S3·librosa·Gemini).
노래방 채점 규칙은 librosa 와 무관한 순수 규칙이라 `domain/services` 에 두고, 음높이 측정만 어댑터에 둔다.

## 노래방 한 판의 흐름

```
[관리자 PC]  완성곡 ─ Demucs ─▶ 보컬 스템 + 반주 스템
                                   │
                                   ▼ 업로드
[백엔드]     보컬 스템 ─ pyin(16kHz, 20ms) ─ 음표로 묶기 ─ 보컬 후처리 ─▶ 정답 음표 (challenge_charts)
             가사 텍스트 + faster-whisper 두 번 ─ 곡 전체 경로 선택 ─▶ 가사 줄 시작 시각

[브라우저]   반주 재생 + 마이크
              ├─ 20ms 마다: YIN 음높이 → 정답 음표와 비교 → 점수·콤보·판정
              ├─ 화면 갱신마다: 캔버스에 음표 흐름과 내 음정 선
              └─ 녹음 (webm) ─ 16kHz WAV 로 변환 ─▶ 제출

[백엔드]     녹음 ─ pyin ─ 같은 규칙으로 다시 채점 ─▶ 최종 점수 (랭킹은 이 값만)
                    └─ Gemini 가 채점 수치를 근거로 코칭 한 줄
```

## 데이터

| 테이블 | 내용 |
|:--|:--|
| `music_challenges` | 곡(제목·설명·원곡 S3 키·유형) |
| `challenge_charts` | 곡 하나의 악보 — 정답 음표(JSON), 가사 줄과 시작 시각, 멜로디·반주 스템 위치, 추출 상태 |
| `challenge_submissions` | 제출(녹음 S3 키, 로그인했으면 사용자) |
| `submission_evaluations` | 평가 — 점수, AI 코칭, 다음 추천 곡, 노래방 서버 채점(음정·박자·종합) |

랭킹은 별도 테이블 없이 평가에서 **사람마다 최고 기록 하나**를 골라 순위를 매긴다(`DISTINCT ON` + `RANK()`).
같은 점수면 먼저 달성한 사람이 위에 보이고 순위 숫자는 같이 나눈다.

## 실행 환경

| | 로컬 개발 | 운영 |
|:--|:--|:--|
| 프론트 | WSL Ubuntu 에서 `next dev` (포트 3100) | 개발 데스크톱에서 빌드해 배포 |
| 백엔드 · DB · Redis | Docker Desktop (`docker-compose.local.yml`) | AWS EC2 — Docker Compose, 메모리 1GB + 스왑 2GB |
| 파일 | S3 (같은 버킷) | S3 |
| 곡 준비 | 관리자 PC 의 Docker (CPU) | — (EC2 메모리 1GB 로는 못 돌린다) |

노래방 모드(마이그레이션 0011~0013 과 곡 준비 도구)는 아직 EC2 에 배포하지 않았다. 배포 전에 nginx 업로드 크기 제한(스템 40MB 이상)과 제출 처리 시간(60초 제한)을 점검해야 한다.

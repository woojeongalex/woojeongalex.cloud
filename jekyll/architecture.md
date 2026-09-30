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
| `flutter/` | OCR 앱 (`app.woojeongalex.cloud`) | Flutter · Tesseract |
| `woojeongai/tools/song_prep/` | 곡 준비 도구 (관리자 PC 에서 실행) | Demucs · faster-whisper · Docker |

백엔드는 앱마다 클린 아키텍처로 나눈다 — `domain`(엔티티·값 객체·규칙) → `app`(유스케이스·포트) → `adapter`(API·DB·S3·librosa·Gemini).
노래방 채점 규칙은 librosa 와 무관한 순수 규칙이라 `domain/services` 에 두고, 음높이 측정만 어댑터에 둔다.

**도메인에 있는 것** — DB 도 FastAPI 도 타지 않아 요인을 하나씩 떼어 확인할 수 있다.

| 파일 | 하는 일 |
|:--|:--|
| `karaoke_scoring.py` | 정답 음표 대비 음정·박자 채점 |
| `vocal_traits.py` | 발성 진단 8종 |
| `next_song.py` | 약점에 맞는 다음 곡 고르기 |
| `rhythm_pattern.py` · `rhythm_scoring.py` | 리듬 게임 채보 생성·판정 |

2026-09-28 에 수업 과제로 만들었던 앱들(`titanic` · `silicon_valley` · `star_craft` 등)을 `lesson/class-projects` 브랜치로 분리했다. 제품에 남은 앱은 `music_challenge` · `music` · `friday13th`(인증) · `ocr` 넷이다.

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
                    ├─ 같은 프레임을 한 번 더 읽어 ─▶ 발성 진단 8종
                    ├─ 점수 + 진단 ─ Gemini ─▶ 코칭
                    └─ 진단의 약점 ─▶ 다음 곡 (음역·빠르기로 고른다)
```

발성 진단은 **녹음을 다시 읽지 않는다.** 채점이 이미 훑고 지나가는 (시각, MIDI) 프레임을
한 번 더 볼 뿐이라 비용이 거의 없다 — 메모리 1GB 짜리 EC2 에서 제출 하나가 수 분씩
걸리던 전례가 있어 새 신호 처리는 붙이지 않았다.

## 데이터

| 테이블 | 내용 |
|:--|:--|
| `music_challenges` | 곡(제목·설명·원곡 S3 키·유형) |
| `challenge_charts` | 곡 하나의 악보 — 정답 음표(JSON), 가사 줄과 시작 시각, 멜로디·반주 스템 위치, 추출 상태 |
| `challenge_submissions` | 제출(녹음 S3 키, 로그인했으면 사용자) |
| `submission_evaluations` | 평가 — 점수, AI 코칭, 다음 추천 곡, 노래방 서버 채점(음정·박자·종합) |
| `rhythm_charts` | 리듬 게임 채보 6개와 BPM. 노트가 수천 개라 객체 대신 배열로 줄여 담는다 |
| `rhythm_plays` | 리듬 게임 기록 |

랭킹은 별도 테이블 없이 평가에서 **사람마다 최고 기록 하나**를 골라 순위를 매긴다(`DISTINCT ON` + `RANK()`).
같은 점수면 먼저 달성한 사람이 위에 보이고 순위 숫자는 같이 나눈다.

## 실행 환경

| | 로컬 개발 | 운영 |
|:--|:--|:--|
| 프론트 | WSL Ubuntu 에서 `next dev` (포트 3100) | Vercel (`woojeongalex.cloud`, 함수는 서울 `icn1`) |
| 백엔드 · DB · Redis | Docker Desktop (`docker-compose.local.yml`) | AWS EC2 — Docker Compose, 메모리 912MB + 스왑 2GB |
| 이 기록 사이트 | Docker 로 `jekyll serve` (포트 4000) | EC2 nginx 정적 파일 (`demo.woojeongalex.cloud`) |
| 파일 | S3 (같은 버킷) | S3 |
| 곡 준비 | 관리자 PC 의 Docker (CPU) | — (EC2 메모리로는 못 돌린다) |

**2026-09-30 에 노래방·리듬 게임을 모두 운영에 올렸다.** 곡 7개가 돌아간다.

코드와 곡 데이터는 따로 움직인다. 스템은 S3, 악보는 DB 에 있어 **배포해도 곡은 따라가지 않는다.**
운영에 곡을 넣으려면 곡 준비 도구를 운영 대상으로 다시 돌려야 한다.

# 앱별 현황

## Titanic — 레퍼런스 앱

상세: `apps/titanic/_docs/CLAUDE.md`

James(업로드) / Walter(조회) 패턴 정본. 모든 신규 앱은 이 구조를 따른다.

## Music — 6개 도메인

| 도메인 | 쓰기 UseCase | 읽기 UseCase | Director |
|--------|-------------|--------------|----------|
| Evaluation | `upload` | — | `evaluation_director` |
| Search (MR) | — | `search` | `search_director` |
| Suggest | `upload` | `read` | `suggest_director` |
| Instrument | `upload` | `search` (카탈로그) | `instrument_director` |
| Speech | `upload` | `read_topics` | `speech_director` |
| Video | `analyze` (+ parser) | — (DB 없음) | `video_director` |

**deps:** `music/adapter/inbound/api/deps/music_deps.py` — 6개 `get_*_use_case` re-export.

### API 요약

| 메서드 | 경로 | Use Case |
|--------|------|----------|
| GET | `/api/songs/search?q=` | `SearchUseCase.search` |
| POST | `/api/music/sing-evaluation` | `EvaluationUseCase.upload` |
| POST/GET | `/api/music/vocal-recommendations` | `SuggestUseCase.upload / read` |
| GET | `/api/music/instrument-catalog` | `InstrumentUseCase.search` |
| POST | `/api/music/instrument-evaluation` | `InstrumentUseCase.upload` |
| GET | `/api/music/speech-topics` | `SpeechUseCase.read_topics` |
| POST | `/api/music/speech-evaluation` | `SpeechUseCase.upload` |
| POST | `/api/music/analyze-video` | `VideoAnalysisUseCase.analyze` |

### 미완 (3차 마이그레이션 예정)

- `sing_evaluations.user_id` — ORM에는 있으나 Neon DB에 컬럼 없음 → POST 503
- ERD v2: `user_vocal_recordings.catalog_song_id` 제거 방향

## Friday13th — 인증

- `signup_router` / `login_router` → `SignupInteractor` / `LoginInteractor`
- `UserEntity` — `users` 테이블, bcrypt
- `role`은 서버에서 `"user"` 고정

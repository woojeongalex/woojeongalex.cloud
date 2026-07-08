# 🎵 Music App: 캐릭터 기반 아키텍처 명세

보컬·악기·스피치 3개 파이프라인을 11개 캐릭터가 레이어별로 담당하는 헥사고날 아키텍처 명세서.  
ERD 정본: `music/_docs/music.md`

---

## 레이어 × 캐릭터 전체 맵

| 캐릭터 | schemas | v1 router | ports/input | ports/output | orm model | pg_repo | deps director | use_cases |
|--------|---------|-----------|-------------|--------------|-----------|---------|---------------|-----------|
| **Bard** | `vocal_bard_searcher_schema.py` | `vocal_bard_searcher_router.py` | `vocal_bard_searcher_use_case.py` | `vocal_bard_searcher_repository_port.py` | `vocal_bard_searcher_model.py` | `list_pg_repository.py` | `search_director.py` | `vocal_bard_searcher_interactor.py` |
| **Mia** | `vocal_mia_recorder_schema.py` | `vocal_mia_recorder_router.py` | `vocal_mia_recorder_use_case.py` | `vocal_mia_maestro_repository_port.py` | `vocal_mia_recorder_model.py` | `evaluation_pg_repository.py` | `evaluation_director.py` | `vocal_mia_recorder_interactor.py` |
| **Maestro** | `vocal_maestro_analyzer_schema.py` | *(response-only)* | — | — | `vocal_maestro_analyzer_model.py` | — | — | *(response-only · interactor 없음)* |
| **Muse** | `vocal_muse_recommender_schema.py` | `vocal_muse_recommender_router.py` | `vocal_muse_recommender_use_case.py` | `vocal_muse_recommender_repository_port.py` | `vocal_muse_recommender_model.py` | `suggest_pg_repository.py` | `suggest_director.py` | `vocal_muse_recommender_interactor.py` |
| **Franz** | `instrument_franz_catalog_schema.py` | `instrument_franz_catalog_router.py` | `instrument_franz_catalog_use_case.py` | — | — | — | `instrument_director.py` | `instrument_franz_catalog_interactor.py` |
| **Andrew** | `instrument_andrew_recorder_schema.py` | `instrument_andrew_recorder_router.py` | `instrument_andrew_recorder_use_case.py` | `instrument_andrew_recorder_repository_port.py` | `instrument_andrew_recorder_model.py` | `instrument_pg_repository.py` | `instrument_director.py` | `instrument_andrew_recorder_interactor.py` |
| **Fletcher** | `instrument_fletcher_tuner_schema.py` | *(response-only)* | — | — | `instrument_fletcher_tuner_model.py` | — | — | *(response-only · interactor 없음)* |
| **Cicero** | `speech_cicero_topic_schema.py` | `speech_cicero_topic_router.py` | `speech_cicero_topic_use_case.py` | — | — | — | `speech_director.py` | `speech_cicero_topic_interactor.py` |
| **Herald** | `speech_herald_recorder_schema.py` | `speech_herald_recorder_router.py` | `speech_herald_recorder_use_case.py` | `speech_herald_recorder_repository_port.py` | `speech_herald_recorder_model.py` | `speech_pg_repository.py` | `speech_director.py` | `speech_herald_recorder_interactor.py` |
| **Oracle** | `speech_oracle_analyst_schema.py` | *(response-only)* | — | — | `speech_oracle_analyst_model.py` | — | — | *(response-only · interactor 없음)* |
| **Lumière** | `speech_lumiere_video_schema.py` | `speech_lumiere_video_router.py` | `speech_lumiere_video_use_case.py` | — | — | — | `video_director.py` | `speech_lumiere_video_interactor.py` |

> **response-only**: 해당 캐릭터의 스키마는 응답 전용(Response schema). 라우터·포트·ORM 없이 mapper에서만 사용.  
> **—**: 해당 레이어에 파일 없음 (인메모리 조회 또는 번들 저장 담당 캐릭터와 공유).

---

## 인터랙터 (use_cases)

ISP 분리로 단일 인터랙터가 복수 포트를 구현. 레이어 맵의 `ports/input` 파일과 1:1 대응되지 않는 점 유의.

| 인터랙터 파일 | 구현 포트 | 담당 캐릭터 |
|---|---|---|
| `vocal_bard_searcher_interactor.py` | `SearchUseCase` | Bard |
| `vocal_mia_recorder_interactor.py` | `EvaluationUseCase` | Mia (Maestro는 response-only) |
| `vocal_muse_recommender_interactor.py` | `SuggestUseCase` | Muse |
| `instrument_franz_catalog_interactor.py` | `InstrumentCatalogUseCase` | Franz |
| `instrument_andrew_recorder_interactor.py` | `InstrumentEvaluationUseCase` | Andrew (Fletcher는 response-only) |
| `speech_cicero_topic_interactor.py` | `SpeechTopicUseCase` | Cicero |
| `speech_herald_recorder_interactor.py` | `SpeechEvaluationUseCase` | Herald (Oracle은 response-only) |
| `speech_lumiere_video_interactor.py` | `VideoAnalysisUseCase` | Lumière |

---

## 1. Vocal 그룹 (`vocal`)

> **흐름:** MR 검색 → 보컬 녹음 제출 → AI 분석 → 추천 배너  
> **ERD:** `song_mr_search_lists` → `sing_evaluations` → `user_vocal_recordings` → `ai_vocal_analyses` → `vocal_recommendations`

---

### Bard (음유시인) — `searcher`

* **역할:** MR 검색·저장
* **연동 ERD:** `song_mr_search_lists`
* **드라마:** 방랑하며 노래로 이야기를 전달하는 음유시인. 사용자가 부르고 싶은 곡을 찾아달라는 요청을 받아 카탈로그를 검색하고, 일치하는 MR 후보 목록을 응답. 검색어마다 `song_mr_search_lists` 행이 INSERT되어 이후 보컬 녹음의 맥락 정본(`mr_search_list_id`)이 됨.
* **스키마:** `SongMrHitResponse`, `SongMrSearchResponse`

---

### Mia (보컬 녹음가) — `recorder`

* **역할:** 보컬 녹음 제출 (입력 측)
* **연동 ERD:** `user_vocal_recordings` (FK → `sing_evaluations`)
* **드라마:** 오디션장에서 있는 힘껏 노래를 부르는 배우 지망생. 클라이언트에서 계산된 음정·박자·등급 점수와 함께 서버로 제출. `mr_search_list_id`와 `input_source`(`mic`|`video`)를 포함하며 3NF 번들 저장을 트리거.
* **스키마:** `VocalEvaluationCreateRequest`

---

### Maestro (지휘자) — `analyzer`

* **역할:** AI 보컬 분석 결과 응답 (response-only)
* **연동 ERD:** `sing_evaluations` (허브 ID), `ai_vocal_analyses` (분석)
* **드라마:** 단 한 번의 제스처로 오케스트라 전체를 통솔하는 지휘자. Mia의 제출 이후 3NF INSERT가 완료되면 `sing_evaluations.id`를 응답. 이후 Muse가 이 ID를 기반으로 동작.
* **스키마:** `VocalEvaluationResponse`

---

### Muse (뮤즈) — `recommender`

* **역할:** 장르·곡 추천 배너 생성·조회
* **연동 ERD:** `vocal_recommendations` (FK → `sing_evaluations`, `ai_vocal_analyses`)
* **드라마:** 예술가에게 영감을 불어넣는 신화 속 뮤즈. Maestro가 발급한 `singEvaluationId`를 받아 `ai_vocal_analyses`를 조인해 발성 패턴을 분석하고, 추천 장르·곡 목록을 응답. 점수 스냅샷은 DB 중복 저장 없이 조인으로 채움.
* **스키마:** `VocalRecommendationCreateRequest`, `VocalRecommendationResponse`

---

## 2. Instrument 그룹 (`instrument`)

> **흐름:** 악기 카탈로그 조회 → 연주 녹음 제출 → 튜닝 분석 결과 반환  
> **ERD:** `instrument_evaluations` → `instrument_recordings` → `instrument_tuning_analyses`

---

### Franz (음악 이론가) — `catalog`

* **역할:** 악기 카탈로그 조회 (인메모리, DB 없음)
* **연동 ERD:** `instrument_catalog.py` 인메모리
* **드라마:** 모든 악기의 이론과 표준 튜닝을 손금 보듯 꿰고 있는 이론가. `GET /api/music/instrument-catalog`에서 악기 목록(기타·피아노) 응답.
* **스키마:** `InstrumentCatalogHit`, `InstrumentCatalogResponse`

---

### Andrew (드러머) — `recorder`

* **역할:** 악기 연주 녹음 제출
* **연동 ERD:** `instrument_recordings` (FK → `instrument_evaluations`)
* **드라마:** 완벽한 연주를 위해 손에 피가 맺히도록 드럼을 두드리는 학생. 튜닝 정확도·음 편차·줄별 측정값을 제출. `POST /api/music/instrument-evaluation` → 3단 INSERT 트리거.
* **스키마:** `InstrumentEvaluationCreateRequest`

---

### Fletcher (지휘자) — `tuner`

* **역할:** 튜닝 분석 결과 응답 (response-only)
* **연동 ERD:** `instrument_evaluations` (허브 ID), `instrument_tuning_analyses` (분석)
* **드라마:** 단 0.1센트의 음정 오차도 용납하지 않는 혹독한 지휘자. Andrew의 제출 이후 3단 저장이 완료되면 `instrument_evaluations.id`를 응답.
* **스키마:** `InstrumentEvaluationResponse`

---

## 3. Speech 그룹 (`speech`)

> **흐름:** 스피치 토픽 조회 → 스피치 녹음 제출 → 피드백 분석 결과 반환 (+ 영상 분석 → 보컬 합류)  
> **ERD:** `speech_evaluations` → `speech_recordings` → `speech_feedback_analyses`

---

### Cicero (로마 연설가) — `topic`

* **역할:** 스피치 주제 목록 조회 (인메모리, DB 없음)
* **연동 ERD:** `speech_catalog.py` 인메모리
* **드라마:** 로마 역사상 가장 위대한 연설가. `GET /api/music/speech-topics`에서 코칭 주제 목록 응답.
* **스키마:** `SpeechTopicHit`, `SpeechTopicsResponse`

---

### Herald (왕의 전령) — `recorder`

* **역할:** 스피치 녹음 제출
* **연동 ERD:** `speech_recordings` (FK → `speech_evaluations`)
* **드라마:** 군중 앞에서 왕의 칙령을 큰 목소리로 낭독하는 전령. 명료도·속도·톤·피드백 포인트를 제출. `POST /api/music/speech-evaluation` → 3단 INSERT 트리거.
* **스키마:** `SpeechEvaluationCreateRequest`

---

### Oracle (신탁의 무녀) — `analyst`

* **역할:** 스피치 피드백 분석 결과 응답 (response-only)
* **연동 ERD:** `speech_evaluations` (허브 ID), `speech_feedback_analyses` (분석)
* **드라마:** 무의식에서 진실을 끌어올려 신탁을 내리는 무녀. Herald의 제출 이후 3단 저장이 완료되면 `speech_evaluations.id`를 응답.
* **스키마:** `SpeechEvaluationResponse`

---

### Lumière (영화 발명가) — `video`

* **역할:** 영상 보컬 분석 (DB 미저장, 보컬 파이프라인 합류)
* **연동 ERD:** DB 테이블 없음
* **드라마:** 필름 한 장 한 장을 분석해 움직이는 그림으로 만들어낸 발명가. `POST /api/music/analyze-video`로 영상을 업로드하면 WAV 변환 → librosa 분석 → 음정·BPM·감정 결과를 반환. 클라이언트는 이 결과를 받아 Mia에게 전달(`inputSource: "video"`)해 보컬 파이프라인으로 합류.
* **스키마:** `VideoVocalAnalysisResponse`

---

## 파이프라인 흐름

```
[보컬 파이프라인]
사용자
 ├─▶ Bard(searcher)    → song_mr_search_lists INSERT   → mr_search_list_id 발급
 ├─▶ Lumière(video)    → 영상→WAV→librosa              → 분석 결과 반환 (DB 없음)
 │         │
 │         ▼ inputSource: "video"
 ├─▶ Mia(recorder)     → 3NF INSERT (sing_evaluations + user_vocal_recordings + ai_vocal_analyses)
 ├─▶ Maestro(analyzer) → sing_evaluations.id 응답
 └─▶ Muse(recommender) → vocal_recommendations INSERT  → 추천 배너 응답

[악기 파이프라인]
사용자
 ├─▶ Franz(catalog)    → instrument_catalog 조회       → 악기 목록 응답 (DB 없음)
 ├─▶ Andrew(recorder)  → 3NF INSERT (instrument_evaluations + instrument_recordings + instrument_tuning_analyses)
 └─▶ Fletcher(tuner)   → instrument_evaluations.id 응답

[스피치 파이프라인]
사용자
 ├─▶ Cicero(topic)     → speech_catalog 조회           → 주제 목록 응답 (DB 없음)
 ├─▶ Herald(recorder)  → 3NF INSERT (speech_evaluations + speech_recordings + speech_feedback_analyses)
 └─▶ Oracle(analyst)   → speech_evaluations.id 응답
```

---

## 설계 원칙

| 원칙 | 적용 |
|------|------|
| **캐릭터 기반 네이밍** | `{group}_{character}_{keyword}_{layer}.py` 전 레이어 일관 적용 |
| **ISP 분리** | `InstrumentInteractor(InstrumentCatalogUseCase, InstrumentEvaluationUseCase)` 등 다중 상속으로 역할 분리 |
| **DTO-only 앱 레이어** | `app/` 레이어에서 ORM 엔티티 import 금지 — ports/use_cases/dtos는 DTO만 |
| **멱등성 Provider** | `dependencies/`: `get_*_repository(db)` + `get_*_use_case(repo=Depends(...))` 두 함수 분리 필수 |
| **response-only 캐릭터** | Maestro·Fletcher·Oracle — 라우터 없음, mapper에서 DTO→Schema 변환만 담당 |
| **인메모리 캐릭터** | Franz·Cicero — DB 없음, `instrument_catalog.py`·`speech_catalog.py` 인메모리 반환 |
| **3NF 번들 저장** | 평가 세션(허브) → 녹음 → AI 분석 3단 INSERT는 pg_repository 내에서 처리 |
| **Pydantic 컨벤션** | `ConfigDict(populate_by_name=True)` + `Field(alias=...)` camelCase API 계약 |

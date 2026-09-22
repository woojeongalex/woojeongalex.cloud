---
title: 개발 로그
nav_order: 5
---

# 개발 로그
{: .no_toc }

git 이력에서 자동으로 만든 기록이다 — 커밋 139개 · 21일 (2026-07-08 ~ 2026-09-22). 최신순.

1. TOC
{:toc}

---

## 2026년 9월

### 2026-09-22 · 커밋 4개

- `db5475f` style: song_prep 스크립트 ruff 규칙 맞춤 (동작 동일 — 곡 #7 결합 결과 바이트 단위 일치)
- `c186cad` feat: 곡 준비 도구(song_prep)와 개발 기록 사이트(Jekyll)
- `e2f58db` feat: 실제 보컬용 정답 멜로디 후처리 (조각 합치기 · 튀는 음 교정)
- `3be75b6` feat: 노래방·연주 모드 — 실시간 채점 화면, 서버 재채점, 랭킹

### 2026-09-21 · 커밋 9개

- `b55927a` feat: 노래방 모드 1단계 — 정답 멜로디 추출 + 가사 타이밍 스튜디오
- `a335e99` feat: 홈·내비게이션을 핵심 루프 중심으로 재구성 (Phase 2)
- `154e27b` feat: 내 도전 기록 · 점수 추이 (GET /music_challenge/submissions/me)
- `3171cd9` feat: 챌린지에 마이크 녹음 제출 추가
- `47bc579` feat: 채점을 librosa 객관 지표 + Gemini 코칭 결합으로 교체
- `0bc921c` feat: 다음 챌린지 추천을 실제 추천으로 교체
- `897080c` feat: 제출물에 사용자 연결 (Phase 1)
- `ab58bfe` fix: Gemini 모델 하드코딩 제거 — 평가가 항상 폴백되던 문제
- `9eeecab` chore: 로컬 개발용 compose 오버라이드 추가

## 2026년 8월

### 2026-08-27 · 커밋 1개

- `ae75e4c` fix: music_challenge ORM 을 SQLModel Field 스타일로 교체

### 2026-08-24 · 커밋 5개

- `6b2b40e` feat(db): music_challenge 테이블 마이그레이션 추가 (20260824_0008)
- `61d7c3a` feat: 운영자용 챌린지 등록 화면 추가 (/music-challenge/new)
- `c92ecc0` feat: MENU 드롭다운에 챌린지(/music-challenge) 진입점 추가
- `1ee5e61` style: music-challenge 컴포넌트 Props 타입을 {ComponentName}Props 로 분리
- `7573563` feat: music_challenge 프론트엔드 화면 추가

### 2026-08-21 · 커밋 1개

- `031f1b3` feat: music_challenge 앱 신규 추가 (헥사고날 아키텍처)

### 2026-08-06 · 커밋 2개

- `989fea7` docs: alexview CLAUDE.md를 라우터로 교체, 내용을 _docs/ 7개 파일로 분리
- `87b5c1f` docs: woojeongai CLAUDE.md를 라우터로 교체, 내용을 _docs/ 9개 파일로 분리

### 2026-08-05 · 커밋 1개

- `e6291d7` fix: Service Worker 자기 언레지스터로 교체, index.html에 SW 강제 제거 추가

### 2026-08-04 · 커밋 11개

- `ac1212a` fix: presigned URL이 리전 엔드포인트로 서명되도록 s3v4+virtual 지정
- `8919c07` perf: OCR S3 왕복 제거·이미지 축소·업로드와 인식 병렬화, presigned URL로 이미지 열람 가능하게
- `1a24ff9` fix: OCR API 엔드포인트를 EC2(aws-api)로 변경
- `55c38c0` fix: OCR 엔진을 Textract에서 Tesseract로 교체 (계정 미구독 대응)
- `6e966c7` fix: app.woojeongalex.cloud CORS 추가, 카메라 dart:html로 교체
- `321fed8` feat: 메인 홈 화면 + 카메라 OCR 기능 추가
- `8c4f0bc` fix: 카카오 모바일 토큰 검증을 user/me 우선으로 변경
- `b2d82b4` debug: 카카오 모바일 토큰 검증 로깅 추가 (임시)
- `971b1f8` fix: auth CORS에 app.woojeongalex.cloud 추가
- `55a3c27` refactor: 디자인 시스템을 alexview/DESIGN.md로 분리
- `de6650e` feat: Flutter 카카오 OAuth 로그인, S3 이미지 업로드, 디자인 시스템 통합

### 2026-08-03 · 커밋 2개

- `97f74c9` feat: 인트로 영상을 실제 콘텐츠로 교체
- `8bac365` feat: Flutter 앱 추가 (인트로 영상·스톱워치·카운터 예제 화면)

## 2026년 7월

### 2026-07-30 · 커밋 2개

- `4249e61` fix: AWS Neo4j 최소 비밀번호 길이 제한으로 인한 크래시 루프 수정
- `3062ae8` feat: AWS docker-compose에 pgvector·neo4j 컨테이너 추가

### 2026-07-28 · 커밋 4개

- `652e46a` docs: LangGraph 하네스 보강 및 Neo4j Docker 전략 문서 추가
- `8687ca7` chore: AWS 배포용 docker-compose.aws.yml 추가
- `b1c5850` feat: 레트로 LangChain 채팅 UI 추가, 시멘틱 라우터를 star_craft로 이전 후 Gemini 연동
- `27a6283` feat: neo4j-graphrag 의존성 추가 및 silicon_valley LangChain 하네스/전략 문서 추가

### 2026-07-24 · 커밋 1개

- `ad1e187` feat: AWS S3 접근용 S3Manager 추가 — Keymaker 기반 자격증명 로딩

### 2026-07-22 · 커밋 11개

- `9cf7212` fix: 소셜 로그인 URL을 auth gateway로 수정
- `f24f6b9` fix: backend startup alembic hanging 제거 — init_engine으로 교체
- `d25d90e` fix: /api/auth/me HS256→RS256 get_current_user 교체 — 소셜 로그인 토큰 검증 호환
- `45b716e` fix: fetch 함수 반환 dict에서 provider 키 제거 — router에서 이미 명시적으로 전달
- `3349c89` fix: auth router except 블록에 exception 로깅 추가
- `f8b9eee` fix: auth 컨테이너 startup시 alembic 마이그레이션 제거 — backend가 담당
- `60590cc` feat: vocal analyzer/recorder/searcher + login event tracking + cloudflared container migration
- `4d0fceb` feat: /db-check require_admin → RS256 RoleChecker(Role.ADMIN)
- `00311ee` fix: rename 1.image_classifier_interactor.py → importable module name
- `b06bb0a` fix: remove duplicate harness file with trailing space
- `ea5a22b` feat: auth gateway — apps/auth, core/security (RS256), core/dependencies, auth_main, docker-compose

### 2026-07-21 · 커밋 6개

- `12a21b7` fix: restore quotes in social-callback page (broken by merge conflict)
- `b39b3e8` feat: add star_craft agent docs and interactors
- `994ac38` feat: RBAC 프론트엔드 — admin role 기반 Admin 메뉴/페이지 접근 제어
- `d1ff80b` feat: RBAC — get_current_user/require_admin 공유 의존성 추가, /db-check 관리자 전용
- `5244ad9` fix: 카카오 토큰 교환 요청에 client_secret 추가
- `ced6c3c` fix: backend 서비스에 env_file 추가하여 루트 .env 로드

### 2026-07-20 · 커밋 4개

- `042ed5b` feat: Naver/Kakao/Google OAuth + JWT Redis session system
- `cd8223b` style: auth 페이지에서 Apple·Instagram 소셜 버튼 제거
- `334ce98` feat: JWT 토큰 저장 및 자동 갱신 프론트엔드 연동
- `42c8a88` feat: JWT + Redis 세션 시스템 추가

### 2026-07-16 · 커밋 23개

- `db9eb0f` star_craft: extract only real list-row content when crawling chart-style pages
- `008c245` style: ruff format star_craft empty-keyword fix
- `b0b4803` star_craft: treat empty keyword as "collect everything" instead of an error
- `b943f89` alexview: move crawler/scraper banner from home to Lesson page as tabs
- `5bf5420` alexview: crawler/scraper banner takes a natural-language command
- `5156dd9` star_craft: make keyword matching case-insensitive
- `356ade0` star_craft: understand natural-language commands via Gemini before crawling
- `fa761e7` alexview: add a crawler/scraper banner to the home page
- `0d637db` star_craft: add submit endpoints for one-shot crawl/scrape from the UI
- `ed7bfef` alexview: switch Titanic page accent color from green to white
- `83b75c8` star_craft: send a User-Agent on crawl/scrape requests
- `497bb88` core: RedisClient loads .env itself instead of relying on load order
- `69caf28` star_craft: switch crawl/scrape output from CSV to JSONL, split by folder
- `2a6940f` Dockerfile: swap opencv-python for opencv-python-headless
- `de81461` star_craft: add boto3/ultralytics -- vision_router's import chain needs both
- `958c2cb` star_craft: fix broken import in vision_provider.py blocking app startup
- `d5a8077` main: register star_craft_router (was never wired into the app)
- `92595ec` star_craft: fix mypy type narrowing in bs4_web_crawl_gateway
- `40a04c8` star_craft: add crawler/scraper pipeline reading targets from Redis
- `b09e2fa` alexview: sync pnpm-lock.yaml after removing @google/generative-ai
- `2c1905d` alexview: remove the weather widget
- `67872f9` alexview+silicon_valley: route the Gemini practice banner through the backend
- `3b4031b` chore: trigger fresh Vercel deployment after reconnecting correct repo

### 2026-07-15 · 커밋 19개

- `a6dbf98` dev: run alexview dev server through WSL where node/pnpm actually live
- `f7c3fb6` silicon_valley: fix person-question misrouting and grounding-quota fallback
- `ddff2b1` silicon_valley: enable Google Search grounding for Gemini general-question path
- `594a76c` alexview: point EXAONE chat banner at the new semantic router endpoint
- `42a40c3` silicon_valley: apply ruff format to semantic router files
- `e945169` silicon_valley: add semantic intent router (music -> local EXAONE, else -> Gemini)
- `809f553` silicon_valley: document that the embed endpoint is a temporary substitute
- `b8ce95a` music: patch EXAONE get/set_input_embeddings for newer transformers/peft
- `35d7dce` music: add QLoRA training script for EXAONE-2.4B music recommendation adapter
- `740d940` music: ground QLoRA dataset generation in real catalog_songs to kill hallucination
- `f09b75b` music: strengthen QLoRA dataset filter (Korean-char ratio, min length, strip)
- `a6adad9` add filter_music_qlora_dataset.py: drop garbled examples, cap dataset size
- `fc487fc` fix: load woojeongai/.env correctly (same off-by-one path bug as backfill script)
- `dc9e29e` fix: proxy routes must not forward raw upstream Response through Cloudflare
- `52ec12d` add generate_music_qlora_dataset.py: synthesize mood-based song recommendation pairs via ship's EXAONE-7.8B for the 2.4B QLoRA fine-tune training set
- `68c41e7` add rag_search_test.py / rag_answer_test.py: hands-on two-step RAG demo
- `ab0b127` fix: backfill script should read LOCAL_LLM_EMBED_BASE_URL, matching the split-endpoint client
- `06b83c5` refactor: RAG chat calls two independent chat/embed endpoints, no runtime mode-switching
- `b4c1122` fix: controller must invoke the vllm console script, not python -m vllm

### 2026-07-14 · 커밋 15개

- `2c20730` silicon_valley: vector RAG chat (EXAONE embed/chat mode swap) + frontend banner
- `da2e724` fix: use core.matrix.database_manager directly (get_session_factory doesn't exist)
- `21556fa` fix: load woojeongai/.env, not the repo-root .env unreachable in the container
- `83c8d4b` fix: backfill script needs both woojeongai root and apps/ on sys.path
- `d0be348` music: add pgvector embedding column to catalog_songs for RAG
- `0ffa787` fix: local LLM client must use vLLM's served-model-name, not the HF repo id
- `185173f` silicon_valley: add local LLM adapter, wire EXAONE chat into Hendricks CEO
- `b5ac295` handoff doc: reflect completed SSH setup + desktop WSL user rename to ship
- `df0018f` handoff doc: auto-detect clone vs pull, inspect code after sync
- `19cc00b` handoff doc: auto-detect clone vs pull, inspect code after sync
- `2eeb2eb` handoff doc: sync latest progress + add git-pull-first instruction
- `2dcdc35` handoff doc: add explicit git-pull-first instruction for next Claude
- `0056327` update infra handoff doc with current progress
- `dd31ba7` add infra handoff doc to friend branch
- `8790f64` alexview: fix homepage jank/scroll, convert theme to grayscale, redesign home/analyze/instrument/speech/auth/admin/mypage; add infra handoff doc

### 2026-07-13 · 커밋 13개

- `350ac45` Make Alembic the sole schema authority; stop raw create_all() on startup
- `e177cde` Drop dead titanic_persons, repoint titanic_bookings FK to titanic_passengers
- `ae5e1ef` Mount woojeongai source into backend container, fix container DATABASE_URL
- `291c1a7` Add users + music domain tables migration
- `23ac23f` Document docker compose exec requirement for alembic/psql commands
- `25cfbd3` Add soccer ERD migration; fix stale ORM import path in alembic env
- `d85c6fa` Add .gitattributes to normalize line endings to LF
- `fc70a2e` Add soccer database design doc
- `0cd763f` Add soccer ERD diagram
- `b10233d` Add soccer app scaffold
- `6238217` Stop tracking .claude/settings.local.json
- `83931fa` Add star_craft vision/yolo scaffolding
- `9889445` Remove frontend service from docker-compose

### 2026-07-10 · 커밋 2개

- `80ca2e5` 7.10.
- `7011ff7` 7.10.

### 2026-07-08 · 커밋 3개

- `3f8e288`  7.8.2.
- `67294a2`  7.8.
- `e9f41b5` Complete Monolithic integration first push

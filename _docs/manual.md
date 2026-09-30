---
name: manual
type: doc
---

# IUEM 설명서

AI 가 만든 곡을 **노래방처럼 부르거나**(음정·박자 채점 + 발성 진단), **리듬 게임으로 치는**(떨어지는 노트) 서비스다.

이 문서 하나로 전체 구조·운영·개발을 파악할 수 있게 썼다. 세부 규칙은 `woojeongai/_docs/`, `alexview/_docs/` 에 있고 여기서 링크한다.

기준일 **2026-09-30**, `main` = `8df2981`.

---

## 1. 무엇을 하는 서비스인가

| 모드 | 하는 일 | 화면 |
|:--|:--|:--|
| **노래방** | 반주에 맞춰 부르면 정답 음표와 대조해 음정·박자를 재고, 발성을 진단해 AI 코칭과 다음 곡을 준다 | `/music-challenge/[id]/play` |
| **리듬 게임** | 떨어지는 노트를 박자에 맞춰 친다. 4키·7키 × 쉬움·보통·어려움 | `/rhythm/[id]` |
| **악보 스튜디오** | 관리자가 곡을 올려 정답 음표와 가사 타이밍을 만든다 | `/music-challenge/[id]/studio` |
| **실험실** | 보컬 분석·악기 튜닝·스피치. **화면만 있고 실측 분석은 아직 안 붙었다** | `/analyze` `/instrument` `/speech` |
| **OCR** | 사진에서 글자를 읽는다. Flutter 앱이 쓴다 | `app.woojeongalex.cloud` |

---

## 2. 저장소 구조

```
woojeongalex.cloud/
├─ woojeongai/     백엔드 (FastAPI · 클린/헥사고날)
├─ alexview/       프론트엔드 (Next.js)
├─ flutter/        OCR 모바일·웹 앱
├─ alexthegreat/   Flutter 실험
├─ jekyll/         개발 로그 블로그
└─ _docs/          모노레포 공통 문서 ← 이 파일
```

### 백엔드 앱 (`woojeongai/apps/`)

| 앱 | 역할 | 주요 경로 |
|:--|:--|:--|
| `music_challenge` | **핵심**. 노래방·리듬 게임·악보·랭킹·AI 채팅 | `/music_challenge/*` |
| `music` | 보컬·악기·스피치 평가(실험실용) | `/api/music/*`, `/api/songs/*` |
| `friday13th` | 인증 — 가입·로그인·소셜·토큰 | `/api/auth/*` |
| `ocr` | 사진 → S3 적재 + Tesseract 글자 인식 | `/ocr/upload` |
| `auth` | RBAC 역할 검사 | (라우터 없음) |

**수업 과제로 만들었던 앱(`titanic` · `silicon_valley` · `star_craft` 등)은 2026-09-28 에 분리했다.** 코드는 `lesson/class-projects` 브랜치에 그대로 있다. 자세한 내용은 [3-2](#3-2-수업-코드-분리).

### 아키텍처

포트와 어댑터. 안쪽(도메인·유스케이스)은 바깥쪽(FastAPI·DB·S3)을 모른다.

```
adapter/inbound/api/   ← HTTP 가 들어오는 곳 (라우터·스키마·매퍼)
app/ports/input/       ← 유스케이스 인터페이스
app/use_cases/         ← 흐름 조립
app/ports/output/      ← 바깥에 요구하는 인터페이스
adapter/outbound/      ← 실제 구현 (PG·S3·Gemini·librosa)
domain/                ← 순수 규칙. 아무것도 import 하지 않는다
dependencies/          ← 조립(Director)
```

규칙 원본: [`woojeongai/_docs/arch-clean-hexagonal.md`](../woojeongai/_docs/arch-clean-hexagonal.md)

**도메인에 있는 것 (DB 없이 검증 가능한 순수 함수)**

| 파일 | 하는 일 |
|:--|:--|
| `karaoke_scoring.py` | 정답 음표 대비 음정·박자 채점 |
| `vocal_traits.py` | 발성 진단 8종 |
| `next_song.py` | 약점에 맞는 다음 곡 고르기 |
| `rhythm_pattern.py` | 리듬 게임 채보 생성 |
| `rhythm_scoring.py` | 리듬 게임 판정 |

---

## 3. 최근에 바뀐 것 (2026-09-28 ~ 30)

### 3-1. 박자·재생 성능

- **비트 격자를 드럼에 맞췄다** (`675daf6`) — 채보가 곡의 실제 박과 0~3.6% 밖에 안 맞던 것을 47~93% 로 올렸다
- **반주를 MP3 로 내려보낸다** (`b33510a`, `a3d7b10`) — 4분짜리 곡이 40MB → 5.4MB. **86% 절감**. 곡을 올리면 ffmpeg 이 자동으로 만든다
- **Vercel 함수를 서울에서 실행** (`7436d58`)

### 3-2. 수업 코드 분리

`7f09f71` · 보존 브랜치 **`lesson/class-projects`**

떼어낸 것: `titanic` `silicon_valley` `star_craft` `agora` `avengers` `doro` `justice_league` `soccer`, 프론트 `/titanic` 구역, 관리자 콘솔, 홈의 "리처드 헨드릭스" 배너.

**앱을 지울 때는 프론트가 그 경로를 타는지 먼저 확인할 것.** 두 번 걸렸다.

| 기능 | 원래 위치 | 옮긴 곳 |
|:--|:--|:--|
| 홈 Gemini 채팅 | `/silicon_valley/gemini/chat` | `/music_challenge/ai/chat` |
| Flutter OCR | `/silicon_valley/s3-image/upload-ocr` | `/ocr/upload` |

### 3-3. 발성 진단과 추천

`b671b78` · `77978e5` · `e21bb0b`

채점이 훑는 (시각, MIDI) 프레임을 **한 번 더 읽어** 발성을 진단한다. 녹음을 다시 읽지 않아 비용이 거의 없다.

재는 것: 소리 낸 비율 · 음정 쏠림 · 어긋난 방향(쳐짐/뜸) · 음 잡는 시간 · 긴 음의 흔들림(비브라토) · 음역별 정확도 · 편한 음역 · 놓친 음표.

이 값이 **AI 코칭 프롬프트**와 **결과 화면 표**, **다음 곡 추천**에 함께 쓰인다.

추천은 이제 ① 악보가 준비된 곡만 ② 편한 음역과 겹치는 곡 ③ 고음/저음이 약하면 그쪽으로 덜 가는 곡 ④ 박자가 약하면 느린 곡을 고른다.

### 3-4. 인증 구멍

`75518f5` — **세션이 끊긴 제출이 조용히 익명으로 저장되던 문제.** 화면은 로그인 상태로 보이고 점수도 나오는데 랭킹에만 안 남았다. 서버를 재시작해 Redis 세션이 비면 로그인한 모든 사용자에게 한꺼번에 일어난다.

토큰을 보냈는데 유효하지 않으면 이제 401 을 낸다. 클라이언트가 갱신해 다시 보내므로 대부분 저절로 복구된다.

---

## 4. 개발 환경 띄우기

### 백엔드

```bash
docker compose -f docker-compose.yaml -f docker-compose.local.yml up -d pgvector backend
```

- 백엔드 `http://localhost:8000`, DB 는 `pgvector_container` 의 `woojeongai`
- `./woojeongai` 를 바인드 마운트하므로 **코드 수정은 uvicorn reload 로 바로 반영**된다

**주의 — Docker 엔진이 둘이다.** Docker Desktop 과 WSL 안 dockerd 가 각각 별개의 볼륨을 갖는다. 이름이 같은 컨테이너라도 **데이터가 다르다.** 어느 쪽인지 헷갈리면 `alembic_version` 을 보면 된다.

### 프론트엔드

`.claude/launch.json` 의 `alexview-win` (포트 3100).

- **HMR 이 안 먹는다** (`/mnt/c` 라서). 코드를 고치면 `.next` 지우고 서버를 다시 띄워야 한다
- `.next` 의 생성 타입이 낡으면 `pnpm type-check` 가 없는 파일을 찾는다며 실패한다

### 로컬 테스트 계정

**testuser1 / Test1234!** (로컬 DB 에서만 admin)

---

## 5. 하네스 (작업 후 필수)

### 백엔드

```bash
cd woojeongai
~/.venvs/lint/bin/ruff check . --fix
~/.venvs/lint/bin/ruff format <고친 파일만>
```

- **ruff·mypy 는 PATH 에 없다.** `~/.venvs/lint/bin/` 을 쓴다
- **`ruff format .` 을 전체에 돌리지 말 것.** 저장소가 포맷돼 있지 않아 무관한 108개 파일이 재포맷된다. 고친 파일만 지정한다
- mypy 전체 실행은 `alembic`/`apps` 중복 모듈 오류로 멈춘다. 파일을 지정해 돌린다:
  ```bash
  MYPYPATH=apps ~/.venvs/lint/bin/mypy --ignore-missing-imports \
    --explicit-package-bases --namespace-packages <파일>
  ```
  기존 오류 6건(SQLModel `table=True`)은 예전부터 있던 것

### 프론트엔드

```bash
cd alexview
pnpm type-check
```

**`CLAUDE.md` 의 `pnpm lint:fix`·`pnpm format` 은 존재하지 않는 스크립트다.** eslint 도 설치돼 있지 않다. 실제로 도는 건 `type-check` 뿐이다.

---

## 6. 곡 추가하기

### 6-1. 리듬 게임 채보 (스템 불필요)

곡을 등록한 뒤 스튜디오에서 "채보 만들기". 원곡에서 박과 소리 시작점을 찾아 6개(4키·7키 × 3난이도)를 자동 생성한다.

### 6-2. 노래방 악보 (보컬 스템 필요)

Suno 스템이 없으면 **Demucs 로 직접 분리**한다.

```bash
# 1) 보컬/반주 분리 — song-prep-demucs:latest (CPU, 곡당 1~3분)
docker run --rm -v <작업폴더>:/data song-prep-demucs:latest \
  demucs --two-stems=vocals -o /data/out /data/song.wav

# 2) 음정 추출 + 가사 정렬 + 업로드
cd woojeongai/tools/song_prep
SONG_PREP_PASSWORD=<비번> python3 prepare_song.py <곡.wav> <가사.txt> \
  --challenge-id <id> \
  --vocals <out/htdemucs/song/vocals.wav> \
  --backing <out/htdemucs/song/no_vocals.wav>
```

가사 정렬은 Whisper **small·medium 두 모델**을 돌려 서로 다른 줄을 "확인 권장"으로 표시한다. 스튜디오에서 눈으로 보고 Space 로 다시 찍으면 된다.

자세한 절차: [`woojeongai/_docs/song-prep-pipeline.md`](../woojeongai/_docs/song-prep-pipeline.md)

**현재 악보가 있는 곡 (7)**: Still Here In The Dark · Close Enough To Touch · 가로등 아래 길게 늘어진 그림자 · the sky · Stay (노래) / My Memories · Sunlight Sparkle (리듬 게임만)

---

## 7. 운영

### 호스트

| 주소 | 정체 |
|:--|:--|
| `woojeongalex.cloud` | 프론트 (Vercel, 함수는 서울 `icn1`) |
| `aws-api.woojeongalex.cloud` | **백엔드** — EC2 nginx → `127.0.0.1:8000` |
| `app.woojeongalex.cloud` | Flutter OCR 웹 |
| `api-backend.woojeongalex.cloud` | 인증서가 없어 526. **쓰지 않는다** |

### EC2

```bash
ssh -i ~/.ssh/woojeongalex-agent-key.pem ec2-user@54.116.178.227
```

- 인스턴스 `i-0378de2b8dc6047c8` (t3.micro, 탄력적 IP)
- 저장소 `/home/ec2-user/projects/woojeongalex.cloud`
- compose `woojeongai/docker-compose.aws.yml`, 서비스 `backend`(host network, 8000) · `pgvector`
- env 는 `woojeongai/.env` (루트에는 없다)
- **RAM 912MB + 스왑 2GB.** 스왑이 없으면 부팅 직후 컨테이너가 메모리를 태워 죽는다
- **neo4j 는 꺼둔 상태** — 메모리를 독식한다

### 배포 절차

```bash
# 1) DB 백업
sudo docker exec pgvector pg_dump -U postgres -Fc woojeongai > ~/db-backups/before_deploy_$(date +%Y%m%d_%H%M).dump

# 2) 코드
cd /home/ec2-user/projects/woojeongalex.cloud && git fetch origin main && git reset --hard origin/main

# 3) 롤백 태그
sudo docker tag woojeongalexcloud-backend:latest woojeongalexcloud-backend:rollback-$(date +%Y%m%d-%H%M)

# 4) 빌드 — buildx 버전 문제로 compose build 는 실패한다
cd woojeongai && sudo DOCKER_BUILDKIT=0 docker build -t woojeongalexcloud-backend:latest .

# 5) 교체
sudo docker compose -f docker-compose.aws.yml up -d --force-recreate backend

# 6) 확인
curl -s -o /dev/null -w "%{http_code}\n" https://aws-api.woojeongalex.cloud/health
```

**되돌리기**: `sudo docker tag woojeongalexcloud-backend:rollback-<날짜> woojeongalexcloud-backend:latest` 후 5번 반복.

**배포 전에 확인할 것**
1. 새 마이그레이션이 있는가 — `git diff --name-only <운영커밋>..main -- woojeongai/alembic/versions/`
2. Dockerfile 이 바뀌었는가 — 바뀌었으면 전체 재빌드(~10분)
3. **없앤 엔드포인트를 누가 부르는가** — Flutter·프론트를 `grep` 할 것

### 곡 데이터는 코드가 아니다

스템은 S3, 악보는 DB 다. 배포해도 따라가지 않는다. 운영에 곡을 넣으려면 6장 절차를 운영 대상으로 다시 해야 한다.

### Flutter 웹 배포

로컬에서 빌드해 scp 로 올린다. **`chmod` 를 빼먹으면 nginx 가 403 을 낸다.**

---

## 8. 걸려 넘어지기 쉬운 것

| 증상 | 원인·대처 |
|:--|:--|
| 페이지가 체감상 느린데 응답은 빠름 | WSL 스왑을 본다. `free -h` 의 Swap used 가 크면 그것이다. `swapoff -a` 뒤 `swapon /dev/sdc` (fstab 에 없어 `swapon -a` 로는 안 켜진다) |
| 화면이 안 바뀜 | `/mnt/c` 라 HMR 이 안 먹는다. `.next` 지우고 dev 서버 재시작 |
| 컨테이너 데이터가 비었음 | Docker 엔진이 둘이다. `alembic_version` 으로 구별 |
| `pgrep -f "이름"` 이 안 끝남 | 감싸는 bash 자신의 명령줄이 걸린다. PID 파일이나 `wait` 를 쓸 것 |
| `docker cp`/`exec` 경로가 깨짐 | MSYS 가 경로를 변환한다. `MSYS_NO_PATHCONV=1` 을 붙인다 |
| 디스크 부족 | 실제 Docker 는 WSL 안(C 드라이브)이다. D 의 Docker Desktop 이 아니다 |

**느리다는 말에 코드부터 고치지 말 것.** 9/28 성능 문제 4건이 전부 코드가 아니었다 — Cloudflare 엣지 경유, WAV 크기, 스왑, 엔진 혼동.

---

## 9. 화면을 사람 없이 확인하는 법

마이크·키보드가 필요한 화면도 브라우저에서 검증할 수 있다.

**노래방** — `navigator.mediaDevices.getUserMedia` 를 가로채 발진기(sine) 스트림을 돌려주고, `MediaRecorder.start()` 시점을 곡 시작으로 잡아 정답 음표대로 "부른다". 일부러 틀리게(예: 고음만 −80센트) 부르면 진단이 그걸 잡아내는지까지 확인할 수 있다.

**리듬 게임** — `audio.currentTime` 을 시계로 삼아 노트 시각에 `KeyboardEvent` 를 쏜다. 이 방식으로 7키 어려움 486노트에서 **1,000,000점 풀 콤보**가 나온다. (합성 키가 안 먹는 게 아니라 시각을 못 맞추면 실패한다)

---

## 10. 남은 일

| | 내용 |
|:--|:--|
| 악보 검수 | Stay·the sky 의 "확인 권장" 줄. 자동 보정으로 9줄 → 2줄까지 줄여 뒀다 |
| 운영 곡 데이터 | 로컬에만 있는 악보 2곡을 운영에 넣어야 한다 |
| 실험실 | `/analyze` `/instrument` `/speech` 는 화면만 있다 |
| titanic 테이블 | 마이그레이션 이력이라 남겼다. 테이블은 DB 에 그대로 있다 |
| 저장소 포맷 | `ruff format` 을 한 번 전체에 돌려 정리할지 정해야 한다 |
| 하네스 문서 | `alexview/CLAUDE.md` 의 없는 스크립트를 고쳐야 한다 |

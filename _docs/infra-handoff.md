# 인프라/SSH 인수인계 문서 (PC 역할 재배치용)

이 문서는 사람이 아니라 **다른 PC에서 이 프로젝트를 이어받는 Claude(AI 어시스턴트)**가 읽고
사용자에게 절차를 안내하기 위한 문서입니다. 사용자는 터미널 명령을 하나씩 안내받아
직접 실행하는 것을 선호하며(여러 줄을 한 번에 주면 복사/붙여넣기 힘들어함), IT 초보자
수준으로 아주 자세하고 천천히 설명해야 합니다.

## 지금 벌어지는 일 (배경)

기존에는 PC 2대로 작업했습니다:
- **데스크탑** (WSL Ubuntu, 리눅스 사용자 `friend`) — 백엔드(Python/FastAPI/Docker) 담당,
  git 브랜치 `friend`
- **노트북** (WSL Ubuntu, 리눅스 사용자 `ship`) — 프론트엔드(Next.js) 담당,
  git 브랜치 `ship`

**지금부터 역할이 바뀝니다:**
- 기존 노트북은 **초기화(은퇴)** — 더 이상 이 프로젝트에 안 씀
- **데스크탑**이 새로운 **`ship`(프론트엔드)** 역할을 맡음
- **새로운 PC 한 대**가 새로운 **`friend`(백엔드)** 역할을 맡음

즉, 물리적으로 데스크탑은 그대로 남지만 용도가 백엔드→프론트엔드로 바뀌고,
새 PC가 데스크탑이 하던 백엔드 역할을 새로 이어받습니다.

## ⚠️ 보안 주의사항 (반드시 읽을 것)

- GitHub 저장소 `woojeongalex/woojeongalex.cloud`는 **Public(공개) 저장소**입니다.
- 이 문서에는 실제 비밀번호, Cloudflare 토큰, API 키 등 **진짜 비밀값을 절대 적지 않습니다.**
  전부 새로 발급해서 안전한 방법(직접 타이핑, 개인 메모 등)으로 전달해야 합니다.
- Cloudflare Tunnel 토큰, SSH 개인키, GitHub Personal Access Token(PAT)은 기존 것을
  재사용하지 말고 **새 PC마다 새로 발급**하는 것을 권장합니다 (특히 노트북은 초기화되므로
  기존 노트북에 있던 SSH 키/토큰은 자동으로 무효화되지 않으니, 나중에 GitHub/Cloudflare에서
  기존 노트북 관련 키·토큰을 직접 폐기하는 것도 고려할 것).

## 지금까지 구축된 인프라 요약

- **도메인**: `woojeongalex.cloud` (가비아에서 구매, 네임서버는 Cloudflare로 이전됨)
- **원격 접속 방식**: 포트포워딩이나 고정 IP 없이, **Cloudflare Tunnel**로 각 PC의 WSL
  SSH(22번 포트)를 외부에 노출. 예: 데스크탑은 `api.woojeongalex.cloud`로 SSH 접속 가능
  (`ssh api.woojeongalex.cloud`, VSCode Remote-SSH도 이 호스트명으로 연결)
- **인증 방식**: 비밀번호 대신 **SSH 키 인증**으로 전환됨 (VSCode Remote-SSH가 비밀번호
  프롬프트를 못 받아서 타임아웃 나는 문제 때문에 필수였음)
- **WSL 환경 특징**: `systemd`가 없는 WSL이라 `sshd`, `cloudflared`, `docker` 데몬이
  **재부팅/WSL 재시작마다 자동으로 안 켜짐** — 매번 수동으로 다시 켜줘야 함 (아래 "알려진
  제약사항" 참고)
- **Git 브랜치**: `main`, `friend`, `ship` 3개. 각 PC는 자기 브랜치에서 작업하고, 컴퓨터를
  바꿀 때마다 최신 상태를 pull/merge해서 동기화
- **docker-compose 서비스** (백엔드 저장소 루트): `backend`(FastAPI+Alembic 실행 환경),
  `pgvector`(PostgreSQL+pgvector extension), `redis`, `n8n`, `pgadmin`, `neo4j`
- **프론트엔드(`alexview`, Next.js)**: 최근 전체 테마를 블랙&화이트로 전환하고, 홈/analyze/
  instrument/speech/auth/admin/mypage 페이지를 모던하게 리디자인 완료. `titanic` 관련
  페이지는 곧 삭제 예정이라 리디자인에서 제외됨

## 새 PC를 "friend"(백엔드)로 처음부터 설정하는 절차

**0단계 — WSL 설치 확인**
```bash
wsl --version
```
WSL2가 없으면 Windows에서 `wsl --install`로 설치 후 Ubuntu 배포판 실행.

**1단계 — 원격 접속용 SSH 서버 켜기**
```bash
sudo service ssh start
```

**2단계 — cloudflared 설치**
```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

**3단계 — Cloudflare 대시보드에서 새 터널 생성**
- [Cloudflare Zero Trust 대시보드](https://one.dash.cloudflare.com) → Networks → Connectors
  → "Create a tunnel" (예: 이름 `ssh-friend-new`)
- 설치 방법에서 **Debian** 선택 (Ubuntu는 Debian 계열)
- "OR run the tunnel manually in your current terminal session only" 아래 명령어의
  **복사 아이콘을 클릭**해서 전체 토큰을 복사 (화면에 `...`으로 잘려 보여도 아이콘 클릭하면
  전체 복사됨)
- 새 PC 터미널에서 백그라운드로 실행:
  ```bash
  nohup cloudflared tunnel run --token <복사한_토큰> > ~/cloudflared.log 2>&1 &
  ```
- 대시보드로 돌아가서 터널 상태가 **Active**로 바뀌는지 확인

**4단계 — 이 터널을 도메인에 연결 (SSH용)**
- 같은 터널의 **"Published application routes"** 탭 → "Add a published application route"
  - Hostname: 원하는 서브도메인 (예: `friend2.woojeongalex.cloud` — 기존 `api.`와 겹치지
    않는 새 이름 권장. 기존 `api.woojeongalex.cloud`는 데스크탑이 계속 쓸 수도 있으니
    충돌 안 나게 새 이름 사용할 것)
  - Service type: `SSH`
  - URL: `localhost:22`

**5단계 — 이 PC(원격 서버) 쪽 SSH 공개키 등록**
사용자가 접속해올 클라이언트(노트북/데스크탑 등)에서 생성한 **공개키**를 이 새 PC의
`~/.ssh/authorized_keys`에 추가해야 비밀번호 없이 접속 가능:
```bash
mkdir -p ~/.ssh
# 클라이언트 쪽 공개키 내용을 여기에 추가
echo "여기에_공개키_내용_붙여넣기" >> ~/.ssh/authorized_keys
```
(클라이언트에 SSH 키가 없으면 클라이언트 쪽에서 `ssh-keygen -t ed25519`로 새로 생성 후
공개키(`id_ed25519.pub`)를 여기로 복사)

**6단계 — 클라이언트(사용자가 접속할 PC)의 SSH config 등록**
클라이언트 PC(Windows)에서 cloudflared 설치:
```powershell
winget install --id Cloudflare.cloudflared
```
`C:\Users\<사용자>\.ssh\config`에 추가:
```
Host friend2.woojeongalex.cloud
  HostName friend2.woojeongalex.cloud
  User <새PC의 리눅스 사용자명>
  ProxyCommand cloudflared access ssh --hostname %h
```

**7단계 — 백엔드 개발 환경 설치**
- Docker: `curl -fsSL https://get.docker.com | sudo sh` (또는 수동으로 `sudo dockerd &`
  실행, WSL에선 systemd 없어서 서비스 자동등록이 안 될 수 있음)
- Git clone:
  ```bash
  git clone https://github.com/woojeongalex/woojeongalex.cloud.git
  ```
- 새 `friend` 브랜치를 만들거나 기존 `friend` 브랜치 체크아웃 (역할이 이 PC로 넘어왔으므로
  기존 `friend` 브랜치를 그대로 이어받는 것을 권장)
  ```bash
  cd woojeongalex.cloud
  git checkout friend
  ```
- `.env` 파일은 git에 없으므로(`.gitignore` 처리됨) `woojeongai/.env.example`이 있으면
  복사해서 새로 값 채우기, 없으면 아래 값들을 참고해 새로 작성:
  `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `REDIS_PASSWORD`,
  `PGADMIN_DEFAULT_PASSWORD`, `N8N_API_KEY` (실제 값은 안전하게 별도 전달받을 것)
- Alembic 마이그레이션 등 DB 관련 명령은 항상 컨테이너 안에서 실행:
  ```bash
  docker compose exec backend alembic upgrade head
  ```

## 데스크탑을 "ship"(프론트엔드)으로 전환하는 절차

데스크탑은 이미 SSH/Cloudflare Tunnel이 살아있으니 네트워크 설정은 그대로 두고, 프론트엔드
개발 환경만 추가하면 됩니다.

1. Node.js 22 + pnpm 설치 확인/설치:
   ```bash
   node -v
   ```
   없으면:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
   sudo apt-get install -y nodejs
   sudo npm install -g pnpm
   ```
2. 저장소가 이미 클론되어 있다면 `ship` 브랜치로 전환:
   ```bash
   cd ~/projects/woojeongalex.cloud
   git fetch --all
   git checkout ship
   git pull
   ```
   (없으면 `git clone https://github.com/woojeongalex/woojeongalex.cloud.git` 먼저)
3. 프론트엔드 의존성 설치:
   ```bash
   cd alexview
   pnpm install
   ```
4. 개발 서버 실행 확인:
   ```bash
   pnpm dev
   ```
   `http://localhost:3000` (또는 WSL2 localhost 포워딩으로 Windows 쪽 브라우저)에서 확인.

## 알려진 제약사항 / 트러블슈팅 (이번 작업 중 실제로 겪은 문제들)

1. **WSL엔 systemd가 없음** — `sudo service ssh start`, `sudo dockerd &`,
   `nohup cloudflared tunnel run --token ... &` 를 컴퓨터를 켤 때마다(또는 WSL 재시작마다)
   수동으로 다시 실행해야 함. `sudo systemctl ...` 명령은 "System has not been booted with
   systemd" 에러가 남.
2. **VSCode Remote-SSH + 비밀번호 인증 조합은 타임아웃 남** — 반드시 SSH 키 인증으로 전환할 것
   (`ssh-keygen` → `authorized_keys`에 공개키 등록).
3. **Windows PowerShell에서 `\\wsl.localhost\...` UNC 경로로 `claude`, `npm`, `node` 같은
   도구를 실행하면 "Exec format error" 또는 cmd.exe UNC 미지원 에러가 남** — 반드시
   VSCode의 **WSL(bash) 터미널**에서 실행할 것 (PowerShell 프로필 말고 Ubuntu/bash 프로필
   선택).
4. **Cloudflare 대시보드에서 토큰 복사할 때, 화면에 `...`으로 잘려 보이는 텍스트를 마우스로
   드래그해서 복사하면 잘린 토큰이 복사됨** — 반드시 옆의 복사 아이콘을 클릭할 것.
5. **git push 시 HTTPS 인증에서 VSCode 내장 credential helper(`vscode-git-*.sock`)가 깨져서
   `ECONNREFUSED` 나는 경우** — `git config --global credential.helper store`로 바꾸고,
   `GIT_ASKPASS` 등 관련 환경변수를 `unset`한 뒤 다시 push하면 터미널에서 직접 아이디/토큰
   입력받아 해결됨.
6. **pnpm은 Node 22.13 이상 필요** — apt 기본 저장소의 Node 18로는 pnpm 설치가 실패하므로
   NodeSource에서 Node 22 설치할 것.

## 이 문서를 읽는 Claude에게

사용자가 이 문서를 보여주면서 "새 PC를 friend로 설정해줘" 또는 "데스크탑을 ship으로
전환해줘"라고 요청하면, 위 해당 섹션을 **한 번에 한 명령씩** 안내하고 결과를 확인받으며
진행하세요. 사용자는 터미널 작업에 익숙하지 않으니 각 단계가 왜 필요한지 짧게 설명을
곁들이는 것이 좋습니다.

# 인프라/SSH 인수인계 문서 (PC 역할 재배치용)

이 문서는 사람이 아니라 **다른 PC에서 이 프로젝트를 이어받는 Claude(AI 어시스턴트)**가 읽고
사용자에게 절차를 안내하기 위한 문서입니다. 사용자는 터미널 명령을 하나씩 안내받아
직접 실행하는 것을 선호하며(여러 줄을 한 번에 주면 복사/붙여넣기 힘들어함), IT 초보자
수준으로 아주 자세하고 천천히 설명해야 합니다.

## 📍 지금 상황 (가장 중요, 먼저 읽을 것)

PC 역할 재배치 작업이 **거의 끝났습니다.** 아래 표가 현재 상태입니다.

| 역할 | 머신 | 상태 |
|---|---|---|
| **friend** (백엔드) | 새 PC, 리눅스 사용자명 `friend2` | ✅ 완료 (SSH·터널·Docker·저장소 다 세팅되고 검증됨) |
| **ship** (프론트엔드) | 데스크탑 (기존엔 `friend` 역할이었음) | ✅ 완료 (Node/pnpm·git ship 브랜치·`pnpm dev` 구동 확인됨). 방금 VSCode + Claude Code(Desktop 앱)를 새로 설치함 |
| (구) 노트북 | — | 아직 초기화 안 함, 나중에 진행 예정 |

**결정 사항**: 새 PC의 리눅스 사용자명은 `friend2`로 계속 유지하기로 함 (`friend`로 이름 변경
안 함 — 이미 Docker/git/터널이 세팅된 뒤라 재설치 리스크가 더 큼).

**지금 당장 해야 할 일**: 데스크탑(ship)에 방금 VSCode + Claude Code를 설치했는데, 아직
`friend2`(새 PC, 백엔드)로 접속하는 SSH 설정이 안 되어 있습니다. 데스크탑의 Windows 쪽에서:

1. cloudflared 설치 (없으면):
   ```powershell
   winget install --id Cloudflare.cloudflared
   ```
2. SSH 키가 없으면 새로 생성 (`ssh-keygen -t ed25519`, 전부 Enter로 기본값)
3. 생성된 공개키(`C:\Users\<사용자>\.ssh\id_ed25519.pub`) 내용을 `friend2` PC의
   `~/.ssh/authorized_keys`에 추가 (SSH로 접속해서 `echo "공개키내용" >> ~/.ssh/authorized_keys`,
   이때는 비밀번호 인증으로 최초 1회 접속 필요)
4. `C:\Users\<사용자>\.ssh\config`에 추가:
   ```
   Host friend2.woojeongalex.cloud
     HostName friend2.woojeongalex.cloud
     User friend2
     ProxyCommand cloudflared access ssh --hostname %h
   ```
5. VSCode에서 Remote-SSH로 `friend2.woojeongalex.cloud` 접속 테스트

`friend2`는 systemd가 있는 최신 WSL이라 sshd/cloudflared/docker가 **재부팅해도 자동으로
켜져 있습니다** (아래 "알려진 제약사항" 1번은 friend2에는 해당 안 됨 — 구 데스크탑/구 노트북
한정 이슈였음).

## 배경 (역할 재배치를 왜 했는지)

기존에는 PC 2대로 작업했습니다:
- **데스크탑** (WSL Ubuntu, 리눅스 사용자 `friend`) — 백엔드(Python/FastAPI/Docker) 담당,
  git 브랜치 `friend`
- **노트북** (WSL Ubuntu, 리눅스 사용자 `ship`) — 프론트엔드(Next.js) 담당,
  git 브랜치 `ship`

역할을 재배치했습니다:
- 기존 노트북은 **초기화 예정** (아직 안 함)
- **데스크탑**이 새로운 **`ship`(프론트엔드)** 역할을 맡음 (물리적으로는 그대로, 용도만 전환)
- **새 PC**(`friend2`)가 새로운 **`friend`(백엔드)** 역할을 맡음

## ⚠️ 보안 주의사항 (반드시 읽을 것)

- GitHub 저장소 `woojeongalex/woojeongalex.cloud`는 **Public(공개) 저장소**입니다.
- 이 문서에는 실제 비밀번호, Cloudflare 토큰, API 키 등 **진짜 비밀값을 절대 적지 않습니다.**
- `friend2`의 `.env`는 개발용 임시값(`devpass1234` 등)으로 채워져 있습니다. 운영 환경이라면
  전부 새로 발급해서 안전하게 교체할 것.

## 지금까지 구축된 인프라 요약

- **도메인**: `woojeongalex.cloud` (가비아에서 구매, 네임서버는 Cloudflare로 이전됨)
- **원격 접속 방식**: 포트포워딩이나 고정 IP 없이, **Cloudflare Tunnel**로 각 PC의 WSL
  SSH(22번 포트)를 외부에 노출.
  - 데스크탑(ship): `api.woojeongalex.cloud`
  - 새 PC(friend2): `friend2.woojeongalex.cloud`
- **인증 방식**: 비밀번호 대신 **SSH 키 인증** (VSCode Remote-SSH가 비밀번호 프롬프트를
  못 받아서 타임아웃 나는 문제 때문에 필수)
- **Git 브랜치**: `main`, `friend`, `ship` 3개. 각 PC는 자기 브랜치에서 작업하고, 컴퓨터를
  바꿀 때마다 최신 상태를 pull/merge해서 동기화
- **docker-compose 서비스** (백엔드 저장소 루트, `friend2`에서 이미 구동/검증됨):
  `backend`(FastAPI+Alembic), `pgvector`(PostgreSQL+pgvector), `redis`, `n8n`, `pgadmin`,
  `neo4j`
- **프론트엔드(`alexview`, Next.js, 데스크탑/ship에서 이미 구동 검증됨)**: 전체 테마를
  블랙&화이트로 전환하고, 홈/analyze/instrument/speech/auth/admin/mypage 페이지를 모던하게
  리디자인 완료. `titanic` 관련 페이지는 곧 삭제 예정이라 제외됨

## 알려진 제약사항 / 트러블슈팅 (실제로 겪은 문제들)

1. **systemd 없는 WSL(구 데스크탑/구 노트북)에선** `sshd`, `cloudflared`, `docker`가
   재부팅마다 자동으로 안 켜짐 — 수동 재시작 필요:
   ```bash
   sudo service ssh start
   nohup cloudflared tunnel run --token <토큰> > ~/cloudflared.log 2>&1 &
   sudo dockerd > /tmp/docker.log 2>&1 &
   ```
   **`friend2`는 systemd가 있어서 이 문제 없음** (`sudo systemctl status cloudflared`,
   `sudo systemctl status docker`, `sudo systemctl status ssh`로 확인 가능, 전부 `enabled`).
2. **VSCode Remote-SSH + 비밀번호 인증 조합은 타임아웃 남** — 반드시 SSH 키 인증으로 전환할 것.
3. **Windows PowerShell에서 `\\wsl.localhost\...` UNC 경로로 `claude`, `npm`, `node` 실행 시
   "Exec format error"** — 반드시 VSCode의 **WSL(bash) 터미널**에서 실행할 것.
4. **Cloudflare 대시보드 토큰은 복사 아이콘 클릭으로만 복사할 것** (드래그로 긁으면 화면에
   `...`으로 잘린 텍스트만 복사됨).
5. **git push 시 HTTPS 인증 문제** (`vscode-git-*.sock` ECONNREFUSED) —
   `git config --global credential.helper store` + `GIT_ASKPASS` 등 관련 환경변수 `unset` 후
   재시도. Username은 GitHub 아이디, Password 자리엔 **Personal Access Token**(진짜 비밀번호
   아님, [github.com/settings/tokens](https://github.com/settings/tokens)에서 `repo` 권한으로
   발급).
6. **pnpm은 Node 22.13 이상 필요** — NodeSource에서 Node 22 설치할 것
   (`curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -`).
7. **`.env` 파일 위치**: `docker compose`는 저장소 **루트**의 `.env`에서 `${VAR}` 치환값을
   읽는다. `woojeongai/.env`에도 별도로 필요할 수 있으니, 안 읽히면 두 곳 다 만들 것
   (`cp woojeongai/.env .env`).
8. **`.next` 폴더가 `root` 소유가 되어 `pnpm dev`가 권한 에러 나는 경우** — 캐시 폴더라
   지워도 안전: `sudo rm -rf .next` 후 재시도.
9. **`newgrp` 명령이 없는 최소 설치 Ubuntu** — `usermod -aG docker <user>` 후 그룹 적용은
   터미널 창을 완전히 닫고 새로 열면 됨 (재로그인 효과).

## 이 문서를 읽는 Claude에게

**0단계 (가장 먼저, 무조건 실행): 최신 코드부터 받아오세요.**
이 문서만으로는 부족합니다 — 지금 작업 중인 저장소 폴더에서 아래를 실행해서 실제 최신
코드/커밋 상태를 먼저 동기화하세요 (이 문서는 인프라 상태만 설명하고, 코드 자체의 진실은
git에 있습니다):
```bash
git fetch --all
git status
git pull
```
만약 이 폴더가 아직 클론되지 않은 새 환경이라면:
```bash
git clone https://github.com/woojeongalex/woojeongalex.cloud.git
cd woojeongalex.cloud
git checkout <이 머신에 맞는 브랜치: ship 또는 friend>
```
그다음 `git log --oneline -10`으로 최근 커밋들을 훑어보고, 이 문서의 "📍 지금 상황"과
실제 코드 상태가 일치하는지 확인한 뒤 사용자에게 다음 단계를 안내하세요.

**1단계**: **가장 위 "📍 지금 상황" 섹션부터 확인하세요.** 대부분의 인프라 설정은 이미 끝났고, 지금
남은 건 데스크탑(ship)의 VSCode에서 friend2로 SSH 접속하는 것뿐입니다. 사용자가 다른 걸
요청하면(예: 새 PC를 처음부터 다시 설정, 노트북 초기화 등) 아래 원 절차를 참고해서 **한
번에 한 명령씩** 안내하고 결과를 확인받으며 진행하세요.

### 참고: 새 PC를 백엔드로 처음부터 설정하는 전체 절차 (friend2 세팅에 실제로 쓴 절차)

1. WSL 설치 확인: `wsl --version` (없으면 `wsl --install`)
2. SSH 서버: `sudo apt update && sudo apt install -y openssh-server && sudo service ssh start`
3. cloudflared 설치:
   ```bash
   curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
   chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/
   ```
4. Cloudflare 대시보드(Zero Trust → Networks → Connectors) → Create a tunnel → Debian 선택
   → "service install" 명령(토큰 포함, 복사 아이콘으로 복사) 실행 → systemd 있으면
   `sudo systemctl status cloudflared`로 확인
5. 터널의 "Published application routes" 탭에서 Hostname 추가, Service Type: SSH,
   URL: `localhost:22`
6. 클라이언트 공개키를 서버의 `~/.ssh/authorized_keys`에 등록
7. 클라이언트(Windows) SSH config에 Host 블록 추가 (`ProxyCommand cloudflared access ssh --hostname %h`)
8. Docker: `curl -fsSL https://get.docker.com | sudo sh` → `sudo usermod -aG docker <user>` →
   터미널 재시작
9. `git clone https://github.com/woojeongalex/woojeongalex.cloud.git` →
   `git checkout friend`(또는 필요한 브랜치)
10. `.env` 작성 (저장소 루트와 `woojeongai/` 양쪽에), `docker compose up -d`로 확인

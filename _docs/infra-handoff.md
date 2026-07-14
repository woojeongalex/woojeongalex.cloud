# 인프라/SSH 인수인계 문서 (PC 역할 재배치용)

이 문서는 사람이 아니라 **다른 PC에서 이 프로젝트를 이어받는 Claude(AI 어시스턴트)**가 읽고
사용자에게 절차를 안내하기 위한 문서입니다. 사용자는 터미널 명령을 하나씩 안내받아
직접 실행하는 것을 선호하며(여러 줄을 한 번에 주면 복사/붙여넣기 힘들어함), IT 초보자
수준으로 아주 자세하고 천천히 설명해야 합니다.

## 📍 지금 상황 (가장 중요, 먼저 읽을 것)

PC 역할 재배치 작업이 **완전히 끝났습니다.** 아래 표가 현재 상태입니다.

| 역할 | 머신 | 상태 |
|---|---|---|
| **friend** (백엔드) | 새 PC, 리눅스 사용자명 `friend2` | ✅ 완료 (SSH·터널·Docker·저장소 다 세팅되고 검증됨) |
| **ship** (프론트엔드) | 데스크탑, WSL 리눅스 사용자명 `ship` (기존 `friend`에서 개명) | ✅ 완료 (Node/pnpm·git ship 브랜치·`pnpm dev` 구동 확인됨. VSCode + Claude Code(Desktop 앱) 설치 및 SSH 설정까지 완료) |
| (구) 노트북 | — | 아직 초기화 안 함, 나중에 진행 예정 |

**결정 사항**: 새 PC(friend2)의 리눅스 사용자명은 `friend2`로 유지 (이미 Docker/git/터널이
세팅된 뒤라 재설치 리스크가 더 큼). **반대로 데스크탑(ship)의 리눅스 사용자명은 `friend` →
`ship`으로 개명 완료** — 이쪽은 재설치 리스크보다 역할과 이름이 일치하는 게 낫다고 판단.
개명 절차는 아래 "WSL 리눅스 사용자명 개명 절차" 섹션 참고 (구 노트북 초기화 시에도 참고할 것).

**SSH 설정 완료 상태**: 데스크탑 → friend2 접속은 **두 경로 모두** 설정 및 검증 완료.
- **Windows 네이티브 쪽** (`C:\Users\<사용자>\.ssh\`): 키 생성 + `friend2` 등록 + config 작성 +
  `ssh friend2.woojeongalex.cloud` 접속 확인됨. VSCode(Windows에서 직접 실행) Remote-SSH로도
  접속 확인됨.
- **WSL(Ubuntu, 사용자 `ship`) 쪽** (`~/.ssh/`): 별도 키 생성 + `friend2` 등록 + config 작성 +
  WSL 터미널에서 `ssh friend2.woojeongalex.cloud` 접속 확인됨.
- VSCode 두 창을 각각 신뢰(Trust Folder)해서 브랜치 표시도 정상화: friend2 쪽 SSH 창은
  `/home/friend2/projects/woojeongalex.cloud`(`friend` 브랜치), 데스크탑 로컬 창은
  `C:\Users\user\Documents\woojeongalex.cloud`(`ship` 브랜치)를 각각 Open Folder로 열어서 연결.

`friend2`는 systemd가 있는 최신 WSL이라 sshd/cloudflared/docker가 **재부팅해도 자동으로
켜져 있습니다** (아래 "알려진 제약사항" 1번은 friend2에는 해당 안 됨). **데스크탑(ship)의 WSL은
systemd가 없어서** cloudflared 터널은 재부팅/재시작마다 수동으로 다시 켜야 함 (아래 1번 참고,
토큰은 `~/.cf_tunnel_token`에 저장해둠 — `nohup cloudflared tunnel run --token $(cat ~/.cf_tunnel_token) > ~/cloudflared.log 2>&1 &`로 재기동).

## 배경 (역할 재배치를 왜 했는지)

기존에는 PC 2대로 작업했습니다:
- **데스크탑** (WSL Ubuntu, 리눅스 사용자 `friend`) — 백엔드(Python/FastAPI/Docker) 담당,
  git 브랜치 `friend`
- **노트북** (WSL Ubuntu, 리눅스 사용자 `ship`) — 프론트엔드(Next.js) 담당,
  git 브랜치 `ship`

역할을 재배치했습니다:
- 기존 노트북은 **초기화 예정** (아직 안 함)
- **데스크탑**이 새로운 **`ship`(프론트엔드)** 역할을 맡음 (물리적으로는 그대로, 용도만 전환).
  WSL 리눅스 사용자명도 `friend` → **`ship`**으로 개명 완료 (git 브랜치명과 일치시킴)
- **새 PC**(`friend2`)가 새로운 **`friend`(백엔드)** 역할을 맡음 (리눅스 사용자명은 `friend2`
  그대로 유지)

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
  못 받아서 타임아웃 나는 문제 때문에 필수). 데스크탑 → friend2 방향은 **Windows 네이티브**와
  **WSL** 양쪽에 각각 별도의 키 페어로 설정 완료 (둘 다 `friend2`의 `~/.ssh/authorized_keys`에
  등록됨).
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
10. **WSL 리눅스 사용자명 개명 시 `/etc/sudoers`에 옛 이름이 남아있음** — `usermod -l`은
    로그인명/홈 디렉터리만 바꾸고 `/etc/sudoers`는 자동으로 안 고쳐줌. 개명 후
    `sudo -n true`가 비밀번호를 요구하면 `grep <옛이름> /etc/sudoers`로 확인하고
    `sed -i 's/^옛이름 /새이름 /' /etc/sudoers` 후 반드시 `visudo -c`로 문법 검증할 것.
11. **사용자명 개명은 그 사용자로 실행 중인 프로세스가 하나도 없어야 됨** (`usermod: user
    X is currently used by process`) — 열려있는 터미널 세션(로그인 쉘)까지 다 걸림. 가장
    확실한 방법은 `wsl --shutdown` (PowerShell)으로 WSL을 완전히 끈 뒤 `wsl -d <배포판> -u
    root`로 들어가서 `usermod`/`groupmod`를 실행하는 것.

### WSL 리눅스 사용자명 개명 절차 (실제로 데스크탑에서 `friend`→`ship` 개명에 쓴 순서)

1. 그 사용자로 떠 있는 프로세스 정리 (dev 서버, cloudflared 터널 등 `kill`), 열려있는
   터미널 세션도 정리
2. PowerShell에서 `wsl --shutdown` (모든 세션 강제 종료 — 남은 로그인 쉘까지 확실히 정리됨)
3. `wsl -d <배포판> -u root -- bash`로 root 진입 후:
   ```bash
   usermod -l 새이름 옛이름
   groupmod -n 새이름 옛이름
   usermod -d /home/새이름 -m 새이름   # 홈 디렉터리 이동, 용량 크면 시간 걸림
   ```
4. `/etc/wsl.conf`의 `[user] default=` 값을 새이름으로 수정
5. `/etc/sudoers`에 옛이름으로 된 항목이 있으면 새이름으로 고치고 `visudo -c`로 검증
   (위 알려진 제약사항 10번 참고)
6. 다시 `wsl --shutdown` 후 `wsl -d <배포판>`으로 들어가서 `whoami`, `echo $HOME`,
   `sudo -n true`로 정상 개명 확인
7. cloudflared 등 systemd 없이 수동으로 띄워뒀던 백그라운드 프로세스 재기동
8. SSH 키·config·`authorized_keys`는 홈 디렉터리 이동에 자동으로 딸려가므로 별도 조치 불필요
   (단, 절대경로를 하드코딩한 스크립트가 있었다면 그건 별도로 확인·수정 필요)

## 이 문서를 읽는 Claude에게

**0단계 (가장 먼저, 무조건 실행): 프로젝트 폴더를 자동으로 받아오고 코드까지 점검하세요.**
이 문서만으로는 부족합니다 — 인프라 상태는 이 문서가 설명하지만, 코드 자체의 진실은 git에
있습니다. 아래 순서로 **폴더가 있든 없든 알아서 처리**한 뒤, 실제 코드까지 훑어보세요.

1. 폴더 존재 여부부터 확인:
   ```bash
   ls -d ~/projects/woojeongalex.cloud 2>/dev/null && echo EXISTS || echo MISSING
   ```
2. **MISSING이면** (이 머신에 처음 클론하는 경우) 새로 클론:
   ```bash
   mkdir -p ~/projects && cd ~/projects
   git clone https://github.com/woojeongalex/woojeongalex.cloud.git
   cd woojeongalex.cloud
   git checkout <이 머신에 맞는 브랜치: ship 또는 friend>
   ```
3. **EXISTS면** (이미 클론된 경우) 최신 상태로 동기화:
   ```bash
   cd ~/projects/woojeongalex.cloud
   git fetch --all
   git status
   git pull
   ```
4. 어느 경우든, 받아온 뒤에는 **커밋 로그만 보고 끝내지 말고 실제 코드 파일까지 열어서
   점검**하세요:
   ```bash
   git log --oneline -10
   ```
   - 프론트엔드(`ship` 브랜치)라면 `alexview/app/`, `alexview/components/`,
     `alexview/app/globals.css`를 실제로 Read해서 지금 테마/구조가 이 문서의 설명과
     일치하는지 확인
   - 백엔드(`friend` 브랜치)라면 `woojeongai/`, `docker-compose.yaml`, `.env`(있는지 여부만
     확인, 내용은 값이 있는지만) 구조를 실제로 확인
   - 이 문서의 "📍 지금 상황"에 적힌 내용과 실제로 열어본 코드 상태가 다르면, 문서보다
     **실제 코드 상태를 우선**하고 사용자에게 차이점을 알려주세요.

**1단계**: **가장 위 "📍 지금 상황" 섹션부터 확인하세요.** 인프라 설정(SSH 양방향, 브랜치 연결,
사용자명 개명)은 전부 끝났습니다. 남은 건 **구 노트북 초기화**뿐입니다. 사용자가 그 작업이나
다른 걸 요청하면(예: 새 PC를 처음부터 다시 설정 등) 아래 원 절차를 참고해서 **한 번에 한
명령씩** 안내하고 결과를 확인받으며 진행하세요. 노트북을 `ship`이 아닌 새 역할로 쓸 계획이면
"WSL 리눅스 사용자명 개명 절차" 섹션도 참고하세요.

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

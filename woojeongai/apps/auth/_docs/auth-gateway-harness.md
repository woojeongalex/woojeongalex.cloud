# Claude Code 작업 지시서 — 인증 게이트웨이(auth.woojeongalex.cloud) 분리 배포

대상 저장소: `woojeongalex.cloud` 모노레포 (`woojeongai/apps/` 클린 아키텍처 구조)
원칙: 기존 구조 무변경, 추가만 허용. 발급은 auth 컨테이너에서만, 백엔드는 검증만.

---

## 0. 컨텍스트

- 현재 `main.py` 하나로 `api-backend.woojeongalex.cloud`에 배포 중.
- `woojeongai/apps/` 하위 앱 목록: `friday13th`(기존 인증), `titanic`, `silicon_valley`, `music`, `star_craft`, `agora`, `avengers`, `doro`, `soccer`, `justice_league`
- 기존 `friday13th` 앱이 OAuth(Kakao/Naver/Google) · JWT · RBAC를 담당 중. 이번 작업으로 `apps/auth/`로 역할을 이관하고 `friday13th`는 signup/login 최소 기능만 유지.
- `core/jwt/jwt_util.py` 에 기존 JWT 유틸이 있음 — 수정 전 반드시 내용 확인 후 보고.
- 목표: 같은 코드베이스에서 엔트리포인트를 분리해 `auth.woojeongalex.cloud`(인증 전용, port 9000)과 `api-backend.woojeongalex.cloud`(비즈니스, port 8000)을 별도 컨테이너로 운영.
- 네트워크: Docker 기본 브리지 네트워크 (현재 docker-compose.yaml에 별도 networks 없음 — 작업 시 `woojeongalex_net` 신규 추가).
- 진입은 cloudflared 터널만. 호스트 포트 미노출.
- 키 체계: RS256 비대칭. 개인키는 auth 컨테이너에만 존재.

---

## 1. 절대 규칙 (위반 시 작업 중단 후 보고)

- `woojeongai/apps/` 하위 기존 앱 코드는 한 줄도 수정하지 않는다.
- 어떤 서비스에도 `docker-compose.yaml`에 `ports:` 매핑을 추가하지 않는다.
- JWT 검증부의 허용 알고리즘은 `algorithms=["RS256"]` 리터럴로 하드코딩한다. 환경변수·설정으로 빼지 않는다.
- 개인키(`JWT_PRIVATE_KEY`)를 읽는 코드는 발급 함수에만 존재해야 한다. 검증 경로에서 개인키 참조 발견 시 즉시 수정.
- 비밀키·개인키를 저장소에 커밋하지 않는다. `.env.*`는 `.gitignore`에 추가.
- 기존 앱들(`friday13th`, `titanic` 등)이 `apps.auth`를 import하는 코드를 작성하지 않는다. 백엔드가 쓸 수 있는 것은 `core.dependencies`뿐.
- `core/jwt/jwt_util.py` 기존 코드는 삭제하지 말고 `deprecated` 주석 처리 후 보고 — 마이그레이션 판단은 사용자 몫.

---

## 2. 작업 목록

### 2.1 `apps/auth/` 신규 생성

```
woojeongai/apps/auth/
├── __init__.py
├── router.py      # POST /login, POST /logout, POST /refresh, GET /callback/{provider}, GET /.well-known/jwks.json
├── services.py    # OAuth Provider 연동(Kakao, Naver, Google), 토큰 발급 오케스트레이션
├── schemas.py     # TokenResponse, LoginRequest, RefreshRequest 등 Pydantic 스키마
└── rbac.py        # Role(str, Enum), Permission 정의, role→permission 매핑 테이블
```

- OAuth Provider 우선순위: Kakao → Naver → Google (기존 friday13th 순서 유지)
- `/.well-known/jwks.json`은 공개키를 JWK 형식(`kid` 포함)으로 반환.
- 리프레시 토큰: Redis(`redis_container`, 내부 호스트명 `redis`) 저장, 로테이션 방식. 재사용 감지 시 해당 사용자 세션 전체 폐기.
- 헥사고날 구조(domain/app/adapter) 적용 여부는 friday13th 패턴 참조 후 사용자에게 확인.

### 2.2 `core/security.py` 신규 생성 (기존 `core/jwt/jwt_util.py` 대체 목적)

```python
# 발급부 — auth 컨테이너 전용 (JWT_PRIVATE_KEY 필요)
def create_access_token(sub: str, roles: list[str], aud: str, expires_min: int = 10) -> str: ...
def create_refresh_token(sub: str) -> str: ...

# 검증부 — 모든 컨테이너 공용 (JWT_PUBLIC_KEY만 필요)
def verify_token(token: str, aud: str) -> TokenPayload: ...
    # jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"], audience=aud)

# 쿠키 설정 — auth 발급 시 사용
COOKIE_KWARGS = dict(
    domain=".woojeongalex.cloud", secure=True, httponly=True, samesite="lax",
)

# 해싱 — auth 전용 (friday13th의 bcrypt 로직 이관)
def hash_password(raw: str) -> str: ...
def verify_password(raw: str, hashed: str) -> bool: ...
```

- 발급 함수는 모듈 로드 시점이 아니라 **호출 시점**에 `JWT_PRIVATE_KEY`를 읽는다. 백엔드 컨테이너에서 모듈 import만으로 키 부재 에러가 나면 안 된다.
- access token 클레임: `sub`, `roles`, `aud`, `exp`, `iat`, `jti`, `kid`(헤더).
- `aud` 값: `woojeongalex-api` (단일 서비스)

### 2.3 `core/dependencies.py` 개선

```python
async def get_current_user(request: Request) -> TokenPayload: ...
    # 쿠키 또는 Authorization 헤더에서 토큰 추출 → verify_token(aud="woojeongalex-api")

class RoleChecker:
    def __init__(self, *allowed: Role): ...
    def __call__(self, user: TokenPayload = Depends(get_current_user)): ...
        # roles 클레임 검사, 미충족 시 403
```

- Redis 블랙리스트 조회(`jti` 기준)를 `get_current_user`에 포함 — 로그아웃/강제 차단 처리용.
- 기존 `friday13th/adapter/inbound/api/deps/current_user_deps.py`의 `require_admin`과 충돌 여부 확인 후 보고.

### 2.4 `auth_main.py` 신규 생성 (루트 `woojeongai/` 하위, `main.py` 옆)

```python
from fastapi import FastAPI
from apps.auth.router import router as auth_router

app = FastAPI(
    title="Woojeongalex Auth",
    docs_url=None, redoc_url=None, openapi_url=None,  # 실서비스: 문서 비노출
)
app.include_router(auth_router, prefix="/auth")

@app.get("/healthz")
async def healthz(): return {"ok": True}
```

### 2.5 `main.py` 확인 (수정 최소화)

- 기존 라우터(`signup_router`, `login_router`, `oauth_router`, `token_router`, `titanic_router`, `silicon_valley_router`, `music_router`, `star_craft_router`) include 구성 유지.
- `apps.auth` import가 없는지 확인만 한다.
- 보호가 필요한 라우터에 `dependencies=[Depends(RoleChecker(Role.USER))]` 적용 예시는 `star_craft_router` 1개에만 적용해 패턴을 보인다.

### 2.6 `docker-compose.yaml` 서비스 추가

```yaml
networks:
  woojeongalex_net:
    driver: bridge

services:
  auth:
    build: ./woojeongai
    command: uvicorn auth_main:app --host 0.0.0.0 --port 9000
    env_file:
      - ./.env.auth          # JWT_PRIVATE_KEY, OAuth client secrets (Kakao/Naver/Google)
    networks: [woojeongalex_net]
    depends_on:
      - redis
      - pgvector
    restart: unless-stopped

  backend:  # 기존 서비스 — env_file만 변경
    env_file:
      - ./.env.backend       # JWT_PUBLIC_KEY만 포함 (개인키 없음)
    networks: [woojeongalex_net]
    # 나머지 기존 설정 유지

  # redis, pgvector, neo4j, n8n, pgadmin 모두 woojeongalex_net 추가
```

- 기존 서비스들 `networks: [woojeongalex_net]` 일괄 추가.
- 기존 루트 `.env` → `.env.auth`(발급용)와 `.env.backend`(검증용)로 분리.
- 두 서비스 모두 `ports:` 없음 유지.

### 2.7 키 생성 스크립트 `scripts/generate_jwt_keys.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
echo "jwt_private.pem → .env.auth 의 JWT_PRIVATE_KEY 로"
echo "jwt_public.pem  → .env.backend 의 JWT_PUBLIC_KEY 로"
```

- PEM 파일은 `.gitignore`에 추가.
- 멀티라인 PEM을 환경변수로 주입 시 base64 인코딩 방식 사용: `base64 -w0 jwt_private.pem`

### 2.8 cloudflared ingress (수동 적용 필요 — 코드 외)

```yaml
ingress:
  - hostname: auth.woojeongalex.cloud
    service: http://auth:9000
  - hostname: api-backend.woojeongalex.cloud
    service: http://backend:8000
  - service: http_status:404
```

```bash
cloudflared tunnel route dns <터널이름> auth.woojeongalex.cloud
```

> ⚠️ Cloudflare 대시보드 → Tunnels → `ssh-woojeongalex.cloud` 터널에 위 route 추가.

### 2.9 `.importlinter` contract 추가

```ini
[importlinter:contract:auth-isolation]
name = apps.auth is only imported by auth_main
type = forbidden
source_modules =
    apps.friday13th
    apps.titanic
    apps.silicon_valley
    apps.music
    apps.star_craft
    apps.agora
    apps.avengers
    apps.doro
    apps.soccer
    apps.justice_league
forbidden_modules =
    apps.auth
```

---

## 3. 완료 기준 (Acceptance Criteria)

- [ ] `uvicorn auth_main:app` 단독 기동 성공, `/healthz` 200.
- [ ] `uvicorn main:app` 기동 시 `JWT_PRIVATE_KEY` 없이 정상 동작 (import 에러 없음).
- [ ] auth에서 발급한 토큰을 backend의 `verify_token`이 공개키만으로 검증 통과.
- [ ] `aud`가 다른 토큰은 검증 실패(403)하는 테스트 존재.
- [ ] 만료 토큰, 서명 변조 토큰, `alg=none`/`HS256` 강제 토큰 각각 거부하는 테스트 존재.
- [ ] 리프레시 토큰 재사용 시 세션 전체 폐기되는 테스트 존재.
- [ ] `lint-imports` 통과 (`auth-isolation` contract 포함).
- [ ] `pytest` 전체 통과. 기존 테스트 회귀 없음.
- [ ] 하네스 게이트 통과: `ruff check . --fix` → `ruff format .` → `mypy . --ignore-missing-imports`

---

## 4. 진행 방식

1. 작업 전 `apps/`, `core/jwt/jwt_util.py`, `main.py`, `friday13th/` 현재 상태를 읽고 요약 보고 후 시작.
2. 커밋 단위: `2.1` → `2.2` → `2.3` → `(2.4+2.5)` → `(2.6+2.7)` → `2.9` 순으로 기능별 분리 커밋.
3. 기존 `core/jwt/jwt_util.py`에 HS256 코드가 있으면 삭제하지 말고 `deprecated` 주석 처리 후 보고.
4. 기존 `friday13th/adapter/inbound/api/deps/current_user_deps.py`의 `require_admin`과 신규 `RoleChecker` 충돌 여부 확인 후 사용자에게 보고.
5. 불명확한 지점(User 모델 스키마, Redis 키 네임스페이스, OAuth provider 콜백 URL 변경 여부)은 추측하지 말고 질문한다.

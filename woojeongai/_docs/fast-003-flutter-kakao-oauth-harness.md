# fast-003 — Flutter 카카오 로그인 백엔드 하네스 (모바일 전용 엔드포인트)

대상: `woojeongai/apps/auth/` (인증 게이트웨이, `router.py` + `services.py` + `schemas.py`).
원칙: 기존 웹 카카오 흐름(`GET /auth/kakao`, `GET /auth/kakao/callback`)은 **한 줄도 수정하지 않는다**.
모바일 전용 엔드포인트를 신규 추가만 한다. 이 문서는 **설계·작업 지시서**이며, 실제 구현 코드는
이 문서에 작성하지 않는다.

프론트엔드(Flutter) 쪽 계약은 [[flutter/_docs/flutter-kakao-oauth-harness|flutter-kakao-oauth-harness.md]] 참조.

---

## 0. 컨텍스트

- `apps/auth/router.py` / `services.py`에 이미 카카오·네이버·구글 **웹** OAuth(코드 교환 방식)가
  구현되어 있다 (`kakao_authorize_url`, `kakao_fetch_user`, `find_or_create_user`,
  `issue_token_pair`).
- `friday13th/adapter/inbound/api/v1/oauth_router.py`에도 동일 로직의 구버전이 남아있다 —
  [[woojeongai/apps/auth/_docs/auth-gateway-harness|auth-gateway-harness.md]]에 따라 `apps/auth`로
  역할이 이관되는 중이며, 이 문서의 작업 대상이 아니다. 건드리지 않는다.
- Flutter 모바일 앱은 카카오 SDK(네이티브)로 로그인해 **access token을 이미 손에 쥔 상태**로 서버에
  온다. 웹처럼 `code`를 받아 `client_secret`으로 교환하는 과정이 없다 — 대신 그 access token이
  "우리 앱이 발급받은 게 맞는지"를 서버가 검증해야 한다.

---

## 1. 왜 웹 콜백과 같은 엔드포인트를 쓰면 안 되는가

| | 웹 (`GET /auth/kakao/callback`) | 모바일 (신규 `POST /auth/kakao/mobile`) |
|---|---|---|
| 입력 | `code` (query param, 리다이렉트로 수신) | `access_token` (JSON body, 앱이 직접 전송) |
| 신원 보증 수단 | `client_secret`으로 code→token 교환 자체가 보증 | access token의 `app_id`가 우리 앱 것인지 별도 검증 필요 |
| HTTP 메서드/응답 | `GET` + `RedirectResponse` (브라우저 리다이렉트) | `POST` + JSON (앱이 파싱) |
| CSRF | `state` 파라미터 필요 | 불필요 (리다이렉트가 없으므로 CSRF 벡터 자체가 없음) |

리다이렉트 응답을 모바일에 그대로 쓰면 앱이 브라우저가 아니므로 처리할 수 없고, 반대로 `code`
교환 로직을 모바일에 쓰면 앱이 애초에 가진 적 없는 `code`를 요구하게 되어 흐름이 성립하지 않는다.
그래서 진입점(엔드포인트)만 분리하고, 그 뒤의 "유저 upsert → JWT 발급"은 기존 함수를 그대로 재사용한다.

```
POST /auth/kakao/mobile   → access token 검증 (신규)
GET  /auth/kakao/callback → code 교환 (기존, 무변경)
        ↓ 둘 다 공통으로 도달
   find_or_create_user(...) → issue_token_pair(user)   (services.py, 이미 존재)
```

---

## 2. 신규 엔드포인트 계약

### 2.1 요청/응답

```
POST /auth/kakao/mobile
Content-Type: application/json

Request:
  { "access_token": "<카카오 SDK가 발급한 access token>" }

Response 200 (TokenResponse — schemas.py에 이미 존재, 재사용):
  { "access_token": "<RS256 JWT>", "refresh_token": "<RS256 JWT>", "token_type": "bearer" }

Response 401:
  - app_id_mismatch   — access_token_info의 app_id가 KAKAO_NATIVE_APP_KEY와 다름
  - token_invalid      — 카카오 API가 토큰을 거부 (만료·변조·폐기됨)
  - profile_failed     — 토큰은 유효하나 프로필 조회 실패
```

새 스키마를 추가할 필요는 없다 — 요청 바디는 필드 하나뿐이라 `schemas.py`에
`KakaoMobileLoginRequest(BaseModel): access_token: str` 하나만 추가하고, 응답은 기존
`TokenResponse`를 그대로 쓴다.

### 2.2 처리 순서 (services.py에 추가할 함수의 책임 — 시그니처만 명시, 구현은 하지 않음)

```
async def kakao_verify_mobile_token(access_token: str) -> dict | None:
    ...
```

책임 범위:

1. `GET https://kapi.kakao.com/v2/user/access_token_info` 를
   `Authorization: Bearer {access_token}` 헤더로 호출한다.
2. 응답의 `app_id`가 환경변수 `KAKAO_NATIVE_APP_KEY`(정수)와 **일치하는지 반드시 검증**한다.
   불일치 시 `None` 반환 (다른 앱이 발급한 토큰을 재사용해 로그인하는 공격을 막는 핵심 검증 —
   생략 금지).
3. 검증 통과 시에만 `GET https://kapi.kakao.com/v2/user/me`로 프로필 조회.
4. 웹 흐름의 `kakao_fetch_user`와 동일한 딕셔너리 형태(`username`, `nickname`, `email`)로 반환해
   `find_or_create_user`에 그대로 넘길 수 있게 한다 — 웹/모바일이 같은 유저 upsert 함수를 공유하되,
   `provider` 인자만 `"kakao_mobile"`로 구분해 `login_events`에서 유입 경로를 구분할 수 있게 한다.
5. 카카오 API 호출은 기존 `_get()` 헬퍼(HTTP GET을 스레드풀로 감싸는 함수, `services.py`에 이미
   존재)를 재사용한다 — 새 HTTP 클라이언트를 만들지 않는다.

### 2.3 라우터 (router.py에 추가할 핸들러 — 시그니처만 명시)

```
POST /kakao/mobile  (router 자체 prefix는 main.py의 include_router에서 "/auth"로 이미 잡혀 있음)
  body: KakaoMobileLoginRequest
  → kakao_verify_mobile_token(body.access_token)
  → None이면 401
  → find_or_create_user(db, provider="kakao_mobile", ip_address=..., **info)
  → issue_token_pair(user)
  → TokenResponse 반환
```

기존 웹 콜백 핸들러(`kakao_login`, `kakao_callback`)와 나란히 "── OAuth — Kakao (모바일) ──"
구획으로 추가한다. 기존 두 함수는 이름·동작 무변경.

---

## 3. 환경변수

| 변수 | 용도 | 비고 |
|------|------|------|
| `KAKAO_CLIENT_ID` | 웹 REST API 키 | 기존 — 무변경 |
| `KAKAO_CLIENT_SECRET` | 웹 code 교환용 | 기존 — 무변경 |
| `KAKAO_REDIRECT_URI` | 웹 콜백 URL | 기존 — 무변경 |
| `KAKAO_APP_ID` | 카카오 콘솔 "앱 설정 > 요약정보"에 표시되는 **숫자 앱 ID** | **신규** — `access_token_info` 응답의 `app_id`와 대조하는 값 |

> **구현 시 정정**: 최초 설계 당시 "Flutter SDK 초기화용 네이티브 앱 키(문자열)"와 대조하는
> 것으로 적었으나, 카카오 `access_token_info` API가 실제로 반환하는 `app_id`는 콘솔의
> **숫자 앱 ID**(네이티브 앱 키와는 다른 값)다. 구현은 `KAKAO_APP_ID`로 정정했다 — 네이티브
> 앱 키는 Flutter SDK 초기화에만 쓰이고 백엔드는 참조하지 않는다.

`KAKAO_APP_ID`는 `.env.auth`(발급 컨테이너 전용, [[woojeongai/apps/auth/_docs/auth-gateway-harness|auth-gateway-harness.md]] §2.6 참조)에 추가한다. 값 자체는 비밀이 아니지만(카카오 콘솔
요약정보 화면에서 누구나 확인 가능), 백엔드 검증 로직이 참조하는 환경이므로 발급 컨테이너와
동일한 곳에 둔다.

---

## 4. 보안 체크리스트

- [ ] `app_id` 검증을 **생략하지 않는다** — 이것이 없으면 아무 카카오 access token으로나 우리
      서비스에 로그인할 수 있게 된다 (다른 앱의 카카오 로그인 토큰 재사용 공격).
- [ ] 카카오 access token은 요청 처리 중에만 메모리에 존재하고, DB·로그에 **저장하지 않는다**.
- [ ] `access_token_info` 실패(만료·변조)와 `app_id` 불일치를 **같은 401 상태코드**로 응답하되
      `detail` 메시지는 구분해도 무방 — 어느 쪽이든 클라이언트 재시도 로직은 "재로그인"으로 동일 처리.
- [ ] 이 엔드포인트에는 `client_secret`을 요구하지도, 받지도 않는다 — 모바일 흐름에 `client_secret`이
      섞여 들어오면 설계가 틀렸다는 신호다.
- [ ] Rate limit: 카카오 API 자체가 호출 제한이 있으므로, 짧은 시간 반복 호출 시 카카오 쪽 429를
      그대로 401로 매핑해 클라이언트에 전달 (재시도 폭주 방지).

---

## 5. 검증 절차

1. `find_or_create_user` / `issue_token_pair` 재사용 여부 확인 — 새로 작성하지 않았는지 diff로 점검.
2. `curl -X POST /auth/kakao/mobile -d '{"access_token":"<유효 토큰>"}'` → 200 + JWT 페어 확인.
3. 만료된 토큰으로 동일 요청 → 401 확인.
4. 다른 카카오 앱(다른 네이티브 앱 키)에서 발급된 access token으로 요청 → `app_id` 불일치로 401
   확인 (이 케이스가 통과하지 않으면 §4 첫 항목이 빠진 것).
5. 기존 `GET /auth/kakao`, `GET /auth/kakao/callback` 회귀 테스트 — 무변경 확인.
6. 하네스 게이트: `ruff check . --fix` → `ruff format .` → `mypy . --ignore-missing-imports`.
7. `pytest` — 신규 엔드포인트에 대해 §5.2~5.4 케이스를 자동화 테스트로 추가.

---

## 6. 완료 기준 (Acceptance Criteria)

- [ ] `POST /auth/kakao/mobile` 신규 추가, 기존 웹 카카오 라우트 무변경
- [ ] `app_id` 검증 로직이 `kakao_verify_mobile_token` 내부에 존재하고 테스트로 강제됨
- [ ] 응답이 기존 `TokenResponse` 스키마 재사용 (신규 응답 스키마 만들지 않음)
- [ ] `find_or_create_user` / `issue_token_pair` 웹·모바일 공통 재사용, 코드 중복 없음
- [ ] `login_events.provider`로 웹(`kakao`)과 모바일(`kakao_mobile`) 유입 경로 구분 가능
- [ ] `KAKAO_NATIVE_APP_KEY` 환경변수 문서화 및 `.env.auth`에만 위치 (커밋 금지)
- [ ] 하네스 게이트(`ruff`, `mypy`) 및 `pytest` 통과

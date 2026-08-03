# Flutter 카카오 로그인 하네스 (모바일 네이티브 SDK)

Flutter 앱(`flutter/`, 패키지명 `taper`)에 카카오 로그인을 붙이는 절차다. **모바일은 웹과 완전히
다른 흐름**을 탄다 — 웹은 브라우저 리다이렉트 기반 authorization code 교환이고, 모바일은 카카오
SDK(네이티브)가 카카오톡 앱 전환 또는 인앱 웹뷰로 로그인해 앱이 access token을 직접 손에 쥔다.
이 문서는 모바일 흐름만 다룬다. 백엔드 계약은
[[woojeongai/_docs/fast-003-flutter-kakao-oauth-harness|fast-003-flutter-kakao-oauth-harness.md]] 참조.

- 기준일: 2026-08-03
- 대상: Flutter 3.44 stable(Dart 3.12), Android/iOS 실기기
- 이 문서는 **설계·작업 지시서**다. 실제 구현 코드는 이 문서에 작성하지 않는다.

---

## 0. 왜 웹과 분리하는가

| 구분 | 모바일 (Flutter 앱) | 웹 (기존 `apps/auth` 구현됨) |
|------|---------------------|-------------------------------|
| 로그인 트리거 | 카카오 SDK → 카카오톡 앱 전환 또는 인앱 웹뷰 | 브라우저를 카카오 인가 페이지로 리다이렉트 |
| 앱이 손에 쥐는 것 | access token(+ 선택적으로 id token) | 없음 — code만 redirect URI로 수신 |
| 토큰 교환 주체 | 이미 SDK가 교환 완료 | 서버가 code + `client_secret`으로 교환 |
| 카카오 콘솔 등록값 | Android 키 해시 / iOS 번들 ID·Custom URL Scheme | 웹 플랫폼 도메인 · Redirect URI |
| CSRF 리스크 | 없음 (리다이렉트 자체가 없음) | 있음 — `state` 파라미터 필수 |
| 백엔드 검증 | access token의 `app_id`가 우리 앱인지 검증 | `client_secret`으로 code 교환 자체가 신원 보증 |

하나의 코드 경로로 합치면 조건 분기가 지저분해지고 검증 포인트를 놓치기 쉬우므로, 진입점(엔드포인트)은
분리하되 "카카오 신원 확정 → 유저 upsert → 자체 JWT 발급" 이후 단계는 백엔드에서 공유한다.

```
Flutter 앱: SDK 로그인 → access token 획득
  → POST /auth/kakao/mobile { access_token } (HTTPS)
서버: access_token_info로 app_id 검증 → 유저 조회/생성 → RS256 JWT(access/refresh) 발급
  → Flutter 앱: 응답의 JWT를 보안 저장소에 저장
```

---

## 1. 패키지·버전 기준선

| 항목 | 값 | 비고 |
|------|-----|------|
| `kakao_flutter_sdk_user` | 최신 stable (pub.dev 기준 조사 후 고정) | 카카오 로그인 전용 최소 패키지. `kakao_flutter_sdk`(전체) 대신 이것만 추가해 번들 크기 최소화 |
| `flutter_secure_storage` | 최신 stable | 우리 서버가 발급한 JWT(access/refresh) 저장용 — `SharedPreferences` 금지(평문) |
| Flutter | 3.44.x stable (Dart 3.12) | [[flutter-android-harness]] 기준선과 동일 |

pubspec.yaml에 위 두 패키지를 추가하는 것이 실제 구현 단계의 1번 작업이다 (본 문서에서는 추가하지 않음).

카카오 SDK 토큰과 우리 서버가 발급한 JWT를 **혼동하지 않는다** — 카카오 access token은 §4의 단발성
전송 후 앱에 남기지 않고, 앱이 실제로 저장·관리하는 것은 우리 서버가 발급한 JWT뿐이다.

---

## 2. 카카오 개발자 콘솔 설정 (모바일 플랫폼 등록)

웹 플랫폼(도메인·Redirect URI)은 이미 등록되어 있다는 전제. 모바일 플랫폼을 **추가** 등록한다.

### 2.1 공통

- 카카오 로그인 활성화 상태에서 "카카오톡으로 로그인" 사용 여부를 확인한다 (앱 미설치 시 웹뷰 폴백은
  SDK가 자동 처리).
- **네이티브 앱 키**(REST API 키와 다른 값)를 발급받아 Flutter 쪽 SDK 초기화에 사용한다. 이 값은
  `client_secret`처럼 다루지 않아도 된다(공개 가능, 앱 바이너리에 포함되는 값).
- 백엔드는 이 네이티브 앱 키를 참조하지 않는다 — 대신 콘솔 "앱 설정 > 요약정보"에 표시되는
  **숫자 앱 ID**(`KAKAO_APP_ID`)를 access token 검증에 사용한다 (백엔드 doc §5 참조). 네이티브
  앱 키와 앱 ID는 서로 다른 값이므로 혼동하지 않는다.

### 2.2 Android

| 항목 | 확인 방법 |
|------|-----------|
| 키 해시 (디버그) | `keytool -exportcert -alias androiddebugkey -keystore ~/.android/debug.keystore \| openssl sha1 -binary \| openssl base64` |
| 키 해시 (릴리스) | 릴리스 서명 키스토어로 동일 명령, 카카오 콘솔에 **별도 등록** 필요 |
| 패키지명 | `flutter/android/app/build.gradle.kts`의 `applicationId`와 일치해야 함 |

카카오 콘솔 → 플랫폼 → Android 플랫폼 등록에 위 키 해시(디버그+릴리스 둘 다)와 패키지명을 입력한다.
키 해시 미등록/불일치 시 `KakaoAuthException(código: -401)` 류 에러로 실패한다.

### 2.3 iOS

| 항목 | 값 |
|------|-----|
| 번들 ID | `flutter/ios/Runner.xcodeproj`의 `PRODUCT_BUNDLE_IDENTIFIER`와 일치 |
| Custom URL Scheme | `kakao{네이티브 앱 키}` 형식, `Info.plist`의 `CFBundleURLSchemes`에 등록 |
| `LSApplicationQueriesSchemes` | `kakaokompassauth`, `kakaolink` 등 카카오톡 판별용 스킴 추가 |

카카오 콘솔 → 플랫폼 → iOS 플랫폼 등록에 번들 ID 입력.

### 2.4 검증

- 카카오 콘솔의 플랫폼 등록 화면에 Android/iOS 항목이 각각 "등록됨" 상태로 표시되면 통과.
- 키 해시 등록 직후 반영까지 수 분 지연될 수 있음 — 즉시 실패해도 재시도.

---

## 3. 앱 초기화 · 매니페스트 설정

실제 구현 시 반영할 항목(코드는 이 문서에 작성하지 않음):

- `main()` 최상단에서 카카오 SDK 초기화 (네이티브 앱 키 전달) — 앱 시작 시 1회만.
- Android `AndroidManifest.xml`: 카카오톡 로그인 리다이렉트를 받을 `intent-filter`(scheme
  `kakao{네이티브 앱 키}`)를 가진 `Activity` 등록.
- iOS `Info.plist`: §2.3의 URL Scheme, `LSApplicationQueriesSchemes` 반영.
- 두 플랫폼 모두 **네이티브 앱 키를 소스에 하드코딩하지 않는다** — `--dart-define` 또는
  플랫폼별 빌드 설정 파일로 주입 (Android `local.properties` / iOS `xcconfig` 등, 저장소에
  커밋되지 않는 경로).

---

## 4. 로그인 플로우 설계

```
1. 사용자가 "카카오로 로그인" 버튼 탭
2. SDK: 카카오톡 설치 여부 확인
   설치됨   → 카카오톡 앱으로 전환 → 로그인/동의 → 앱 복귀
   미설치됨 → 인앱 웹뷰로 카카오 계정 로그인
3. SDK가 OAuthToken(access token, 필요 시 id token, 만료시각) 반환
4. Flutter 앱: access token을 HTTPS POST body로 백엔드 /auth/kakao/mobile 전송
   (카카오 access token 자체는 클라이언트에 영구 저장하지 않는다)
5. 백엔드: app_id 검증 → 유저 조회/생성 → 우리 서버 JWT(access/refresh) 발급 → 응답
6. Flutter 앱: 응답받은 JWT를 flutter_secure_storage에 저장, 이후 API 호출은 이 JWT 사용
```

**실패/취소 케이스별 UX**

| 케이스 | SDK 신호 | 앱 동작 |
|--------|----------|---------|
| 사용자가 로그인 취소 | `KakaoAuthException` (사용자 취소) | 에러 토스트 없이 로그인 화면 유지 (정상 흐름) |
| 카카오톡 미설치 + 네트워크 없음 | 웹뷰 로드 실패 | 네트워크 오류 안내 |
| 백엔드 app_id 검증 실패 (401) | HTTP 401 | "로그인 처리 중 오류" 안내 + 재시도 버튼, 카카오 재로그인 유도하지 않음 (설정 문제이므로 재시도해도 동일 실패) |
| 백엔드 JWT 만료 (평상시 앱 사용 중) | API 401 | refresh 엔드포인트로 자동 갱신 시도 → 실패 시 로그인 화면으로 |

---

## 5. 백엔드 연동 계약

전체 스펙은 [[woojeongai/_docs/fast-003-flutter-kakao-oauth-harness|fast-003-flutter-kakao-oauth-harness.md]] 정본. 여기서는 Flutter 쪽이 알아야 할 요약만 둔다.

```
POST /auth/kakao/mobile
Content-Type: application/json
Body: { "access_token": "<카카오 SDK가 반환한 access token>" }

200 OK
{ "access_token": "<우리 서버 JWT>", "refresh_token": "<우리 서버 refresh JWT>", "token_type": "bearer" }

401 Unauthorized  — app_id 불일치 / 토큰 만료 / 유효하지 않은 토큰
```

- 이후 모든 API 호출은 `Authorization: Bearer <access_token>` (우리 서버 JWT). 카카오 토큰은
  이 한 번의 교환 이후 앱에서 참조하지 않는다.
- refresh는 기존 웹 흐름과 동일한 `POST /auth/refresh`를 공유한다 (모바일 전용 refresh 엔드포인트
  불필요 — JWT 발급 이후 단계는 플랫폼 무관).

---

## 6. 검증 절차

1. `flutter analyze` / `dart format --set-exit-if-changed .` 통과 (하네스 게이트).
2. 실기기(Android/iOS)에서 로그인 버튼 탭 → 카카오톡 전환 또는 웹뷰 → 로그인 → 앱 복귀까지 수동 확인.
3. 카카오톡 미설치 기기(또는 앱 강제 종료 상태)에서 웹뷰 폴백 경로 확인.
4. `adb logcat`(Android) 또는 Xcode 콘솔(iOS)에서 SDK 콜백이 앱으로 정상 복귀하는지 확인 —
   Custom URL Scheme 미등록 시 카카오톡에서 앱으로 돌아오지 못하고 멈춘다.
5. 백엔드 `/auth/kakao/mobile` 응답의 JWT로 보호된 엔드포인트(`/auth/me` 등) 호출이 200인지 확인.
6. 로그아웃 후 `flutter_secure_storage`에 JWT가 남아있지 않은지 확인.

---

## 7. 완료 기준 (Acceptance Criteria)

- [ ] Android 키 해시(디버그+릴리스) · iOS 번들 ID/URL Scheme 카카오 콘솔 등록 완료
- [ ] 네이티브 앱 키가 소스에 하드코딩되지 않고 빌드 설정으로 주입됨
- [ ] 카카오톡 앱 전환 로그인 / 웹뷰 폴백 로그인 둘 다 실기기에서 성공
- [ ] 로그인 취소 시 에러 토스트 없이 정상 복귀
- [ ] 카카오 access token이 앱에 영구 저장되지 않음 (교환 직후 폐기)
- [ ] 우리 서버 JWT만 `flutter_secure_storage`에 저장됨
- [ ] 로그아웃 시 저장된 JWT 완전 삭제
- [ ] `dart analyze --fatal-infos`, `dart format --set-exit-if-changed .` 통과

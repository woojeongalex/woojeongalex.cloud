# Flutter 안드로이드 실기기 개발 하네스

안드로이드 **실제 기기**를 이 저장소의 Flutter 앱(`flutter/`, 패키지명 `taper`)에 연결해
빌드·실행·핫리로드까지 확인하는 절차다. 각 단계마다 **검증 명령**을 두어, "된 것 같다"가 아니라
명령의 출력으로 성공을 판정한다.

- 기준일: 2026-07-31
- 대상: Flutter 3.44 stable(Dart 3.12) / Android Studio Quail(2026.1) / Android 11~17 실기기
- 연결 방식: **USB 데이터 케이블**(개발 PC ↔ 폰) 또는 **Wi-Fi 무선 디버깅**

---

## 0. 버전 기준선

이 프로젝트가 실제로 요구하는 값이다. 문서와 저장소가 어긋나면 저장소가 기준이다.

| 항목 | 값 | 확인 위치 |
|------|-----|-----------|
| Flutter | 3.44.x stable (Dart 3.12) | `flutter --version` |
| Dart SDK 제약 | `^3.10.8` (Dart 3.12 포함됨 — 수정 불필요) | `pubspec.yaml` |
| Android Gradle Plugin | 8.11.1 | `android/settings.gradle.kts` |
| Kotlin | 2.2.20 | `android/settings.gradle.kts` |
| Gradle Wrapper | 8.14 | `android/gradle/wrapper/gradle-wrapper.properties` |
| Java(소스/타깃 호환성) | 17 | `android/app/build.gradle.kts` |
| compileSdk | **36** (Android 16) | Flutter SDK 기본값 `flutter.compileSdkVersion` |
| targetSdk | **36** (Android 16) | Flutter SDK 기본값 `flutter.targetSdkVersion` |
| minSdk | **24** (Android 7.0 Nougat) | Flutter SDK 기본값 `flutter.minSdkVersion` |
| NDK | 28.2.13676358 | Flutter SDK 기본값 `flutter.ndkVersion` |

Flutter 3.44가 지원하는 안드로이드 범위는 **API 24~37**(Android 7.0 ~ Android 17)이며,
API 23 이하는 지원하지 않는다. 옛 자료에 나오는 `minSdk 16/21`, `compileSdk 33/34`,
"Android 4.1 이상이면 USB 디버깅 가능" 같은 서술은 지금 기준으로 전부 유효하지 않다.

> **Google Play 요건**: 2026-08-31부터 신규 앱과 업데이트는 **targetSdk 36(Android 16) 이상**이어야
> 등록된다. Flutter 3.44 기본값이 이미 36이므로 `android/app/build.gradle.kts`에서
> `targetSdk`를 하드코딩해 낮추지 않는 한 요건을 만족한다.

`build.gradle.kts`의 값은 숫자를 직접 쓰지 말고 `flutter.*` 프로퍼티를 그대로 둔다.
Flutter SDK를 올리면 자동으로 따라 올라간다.

---

## 1. 개발 PC 툴체인

### 1.1 설치 대상

| 구성 요소 | 버전 | 비고 |
|-----------|------|------|
| Flutter SDK | 3.44 stable | `git clone -b stable` 또는 공식 아카이브 |
| Android Studio | Quail(2026.1) 계열 최신 스테이블 | JDK 21(JetBrains Runtime) 번들 포함 |
| Android SDK Platform | **API 36** | compileSdk와 일치해야 한다 |
| Android SDK Platform-Tools | 최신 (adb 37.x 이상) | 무선 디버깅 mDNS에 필요 |
| Android SDK Build-Tools | 최신 | |
| Android SDK Command-line Tools | 최신 | `flutter doctor --android-licenses`에 필수 |
| NDK (Side by side) | 28.2.13676358 | 네이티브 플러그인 사용 시 |
| Google USB Driver | 최신 | **Windows에서 USB 연결할 때만** |

Android Studio에서: `Settings`(Ctrl+Alt+S) → `Languages & Frameworks` → `Android SDK` →
`SDK Platforms` 탭에서 API 36, `SDK Tools` 탭에서 위 도구들을 체크하고 `Apply`.

Google USB Driver는 `SDK Tools` 탭 목록에 **Windows에서만** 표시된다. macOS·Linux·WSL에는
항목 자체가 없으며 필요하지도 않다.

### 1.2 검증

```bash
flutter --version          # Flutter 3.44.x / Dart 3.12.x
flutter doctor -v          # [✓] Flutter, [✓] Android toolchain
flutter doctor --android-licenses   # "All SDK package licenses accepted."
adb --version              # Android Debug Bridge version 1.0.4x / 37.x 이상
```

`flutter doctor`에서 Android toolchain에 X가 뜨면 아래를 확인한다.

```bash
flutter config --android-sdk <SDK 경로>   # 자동 탐지 실패 시에만
flutter config --jdk-dir <JDK 경로>       # Android Studio 번들 JDK 경로 권장
```

`adb`가 PATH에 없으면 platform-tools 경로를 PATH에 추가한다.

- Windows: `%LOCALAPPDATA%\Android\Sdk\platform-tools`
- Linux/WSL: `$HOME/Android/Sdk/platform-tools`
- macOS: `$HOME/Library/Android/sdk/platform-tools`

**성공 기준**: `flutter doctor`의 Android toolchain 항목이 `[✓]`이고 라이선스가 모두 수락됨.

---

## 2. 기기 준비 — 개발자 옵션 (USB·무선 공통)

### 2.1 개발자 옵션 활성화

`빌드 번호`를 7번 연속 탭한다. 경로는 안드로이드 버전이 아니라 **제조사 스킨**에 따라 다르다.

| 스킨 | 경로 |
|------|------|
| Pixel / AOSP (Android 12~17) | 설정 → 휴대전화 정보 → 빌드 번호 |
| Samsung One UI | 설정 → 휴대전화 정보 → 소프트웨어 정보 → 빌드 번호 |
| Xiaomi HyperOS / MIUI | 설정 → 내 기기 → 전체 사양 → OS 버전 |
| 그 외 | 설정에서 "빌드 번호" 검색 |

잠금화면 PIN·패턴이 설정돼 있으면 입력을 요구한다.

### 2.2 USB 디버깅 켜기

| 스킨 | 경로 |
|------|------|
| Pixel / AOSP | 설정 → 시스템 → 개발자 옵션 → USB 디버깅 |
| Samsung One UI | 설정 → 개발자 옵션(목록 최하단) → USB 디버깅 |
| Xiaomi | 설정 → 추가 설정 → 개발자 옵션 → USB 디버깅 |

무선만 쓸 경우에도 같은 화면의 **무선 디버깅**을 켜면 되며, USB 디버깅은 필수가 아니다.

### 2.3 검증

기기에서 개발자 옵션 진입이 되고 `USB 디버깅` / `무선 디버깅` 항목이 보이면 통과.

---

## 3. USB 데이터 케이블로 연결하기

여기서 "USB"는 **폰과 개발 PC를 물리 데이터 케이블로 잇는 것**을 말한다.
충전 전용 케이블은 데이터 라인이 없어 인식되지 않는다 — 인식 실패의 가장 흔한 원인이다.

### 3.1 절차

1. (Windows만) Android Studio에서 **Google USB Driver**를 설치한다.
   Pixel·Nexus 계열은 이 드라이버로 충분하고, Samsung·Xiaomi 등은 제조사 USB 드라이버가
   따로 필요할 수 있다.
2. 데이터 케이블로 폰과 PC를 연결한다.
3. 폰에 뜨는 **"USB 디버깅을 허용하시겠습니까?"** 대화상자에서
   `이 컴퓨터에서 항상 허용`을 체크하고 허용한다. (RSA 지문 승인)
4. 대화상자가 안 뜨면 알림창의 USB 연결 모드를 `충전`에서 **`파일 전송(MTP)`**으로 바꾼다.

### 3.2 검증

```bash
adb devices -l
# 예: R3CN90XXXXX   device product:xxx model:SM_S928N device:xxx
```

- `unauthorized` → 폰의 승인 대화상자를 아직 수락하지 않은 상태.
- `offline` → `adb reconnect offline` 후 재확인.
- 목록이 비어 있음 → 케이블·드라이버·USB 모드 순으로 점검(§7).

```bash
cd flutter
flutter devices     # 연결된 기기가 android-arm64 등으로 나열되어야 한다
```

**성공 기준**: `adb devices`에 상태가 `device`로 표시되고 `flutter devices`에 잡힌다.

---

## 4. Wi-Fi 무선 디버깅

Android 11(API 30) 이상은 케이블 없이 페어링할 수 있다. 이 방식이 현재 표준이며,
옛 자료의 `adb tcpip 5555` 방식은 Android 10 이하 전용 폴백이다.

### 4.1 전제

- 폰과 개발 PC가 **같은 네트워크(같은 서브넷)** 에 있어야 한다.
  게스트 Wi-Fi, AP 격리(AP isolation)가 켜진 공유기에서는 실패한다.
- Platform-Tools가 최신(adb 37.x 이상)이어야 한다.

### 4.2 페어링 (최초 1회)

폰: 설정 → 개발자 옵션 → **무선 디버깅** → 켜기 → **페어링 코드로 기기 페어링**
→ IP·포트·6자리 코드가 표시된다.

```bash
adb pair 192.168.0.42:41253      # 화면의 "IP:포트"
# Enter pairing code: 123456     # 화면의 6자리 코드
# Successfully paired to ...
```

Android Studio의 `Device Manager` → `Pair using Wi-Fi`로 **QR 코드 스캔** 페어링도 가능하다.

### 4.3 접속

무선 디버깅 화면 상단에 표시되는 **기기 IP:포트**(페어링 포트와 다르다)로 접속한다.

```bash
adb connect 192.168.0.42:37129
adb devices -l                    # 192.168.0.42:37129  device
```

Android 17 이상은 ADB Wi-Fi 2.0을 지원해, 한 번 페어링하면 신뢰된 네트워크에서 자동 재연결된다.
Android 11~16은 재부팅·네트워크 변경 시 `adb connect`를 다시 실행해야 한다(페어링은 유지된다).

빠른 설정 타일에 **무선 디버깅** 타일을 추가해 두면 매번 설정 앱을 열지 않아도 된다.

### 4.4 Android 10 이하 폴백

```bash
adb tcpip 5555                    # 케이블 연결 상태에서 실행
adb connect <폰 IP>:5555          # 케이블 분리 후
```

### 4.5 무선 연결이 안 될 때

```bash
adb server-status                 # mdns_enabled: true 여야 한다
export ADB_MDNS=1 && adb kill-server && adb start-server
adb mdns track-services --proto-text
```

**성공 기준**: 케이블을 뽑은 상태에서 `adb devices`에 `IP:포트  device`가 유지된다.

---

## 5. WSL 환경 주의 (이 저장소에 해당)

이 저장소는 WSL2(Ubuntu) 파일시스템(`\\wsl.localhost\Ubuntu\home\messi\...`)에 있다.
Windows 쪽 Flutter로 이 경로를 직접 빌드하면 9p 파일시스템을 경유해 Gradle이 매우 느려지고
파일 잠금 문제가 생긴다. 두 가지 방식 중 하나로 정리한다.

**권장 — WSL 안에 리눅스판 툴체인 + 무선 디버깅**

1. WSL에 Flutter(Linux)·Android SDK(cmdline-tools)를 설치한다. Android Studio GUI 없이
   `sdkmanager`만으로도 된다.
2. `%USERPROFILE%\.wslconfig`에 미러 네트워킹을 설정하고 `wsl --shutdown`으로 재시작한다.

   ```ini
   [wsl2]
   networkingMode=mirrored
   ```

3. WSL 셸에서 §4의 `adb pair` / `adb connect`를 그대로 쓴다. USB 패스스루가 필요 없다.

**대안 — USB 케이블을 WSL로 넘기기 (usbipd-win)**

```powershell
# Windows 관리자 PowerShell
winget install --exact dorssel.usbipd-win
usbipd list                                  # Android 기기의 BUSID 확인
usbipd bind --busid <BUSID>                  # 최초 1회
usbipd attach --wsl --busid <BUSID>          # 연결할 때마다
```

- 기기를 재부팅하거나 fastboot 모드로 전환하면 VID:PID가 바뀌므로 bind/attach를 다시 해야 한다.
- WSL 네트워킹은 `mirrored`를 유지한다. `bridged` 모드에서는 usbipd가 동작하지 않는다.
- WSL 쪽에 `adb`가 설치돼 있어야 하고, udev 규칙이 없으면 기기가 `no permissions`로 뜬다.

> Windows에서 개발할 거라면 저장소를 `C:\` 아래로 옮기는 편이 낫다. 지금 구조를 유지한 채
> Windows Flutter로 빌드하는 조합은 권장하지 않는다.

---

## 6. 앱 실행과 검증

```bash
cd flutter
flutter pub get
flutter devices                       # 대상 기기 ID 확인
flutter run -d <device-id>            # 디버그 실행
```

실행 후 콘솔에서 `r`(핫리로드) / `R`(핫리스타트) / `q`(종료).

```bash
flutter run -d <device-id> --profile  # 성능 측정용
flutter run -d <device-id> --release  # 릴리스 동작 확인(현재 debug 키로 서명됨)
flutter build apk --debug             # 빌드만 검증
flutter analyze                       # 정적 분석
flutter test                          # 단위/위젯 테스트
```

`android/app/build.gradle.kts`의 릴리스 빌드는 아직 **debug 키로 서명**된다(템플릿 상태).
스토어 배포 전에 별도 서명 설정이 필요하며, 이 문서의 범위는 아니다.

**성공 기준**: 실기기에 앱이 설치·실행되고, `lib/main.dart`를 수정한 뒤 `r`을 누르면
1초 내에 화면에 반영된다.

---

## 7. 트러블슈팅

| 증상 | 원인 | 조치 |
|------|------|------|
| `adb devices`가 비어 있음 | 충전 전용 케이블 | 데이터 케이블로 교체 |
| 〃 | Windows 드라이버 없음 | Google USB Driver 설치, 제조사 드라이버 확인 |
| 〃 | USB 모드가 충전 | 알림창에서 `파일 전송(MTP)` 선택 |
| `unauthorized` | RSA 승인 안 함 | 폰의 허용 대화상자 수락. 안 뜨면 개발자 옵션 → `USB 디버깅 승인 취소` 후 재연결 |
| `offline` | adb 세션 꼬임 | `adb reconnect offline` → `adb kill-server && adb start-server` |
| `flutter devices`엔 없고 `adb devices`엔 있음 | Flutter가 다른 SDK를 봄 | `flutter doctor -v`의 SDK 경로 확인, `flutter config --android-sdk` |
| 무선 페어링 실패 | 다른 서브넷 / AP 격리 | 같은 Wi-Fi SSID 사용, 공유기 AP 격리 해제 |
| 무선 연결이 자꾸 끊김 | Android 16 이하는 자동 재연결 미지원 | `adb connect`로 재접속, Wi-Fi 절전 옵션 해제 |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | 서명이 다른 동일 패키지가 설치돼 있음 | `adb uninstall com.example.taper` 후 재실행 |
| `minSdkVersion` 오류 | 기기가 Android 7.0 미만 | 지원 대상 아님(API 24 미만) |
| Gradle 빌드가 비정상적으로 느림 | WSL 경로를 Windows에서 빌드 | §5 참고 |

---

## 8. 완료 기준 체크리스트

- [ ] `flutter --version`이 3.44.x / Dart 3.12.x를 출력한다.
- [ ] `flutter doctor`의 Android toolchain이 `[✓]`이고 라이선스가 모두 수락됐다.
- [ ] Android SDK Platform **API 36**과 최신 Platform-Tools가 설치돼 있다.
- [ ] 기기에서 개발자 옵션과 USB(또는 무선) 디버깅이 켜져 있다.
- [ ] `adb devices -l`에 기기가 `device` 상태로 표시된다.
- [ ] 무선 방식이면 케이블 분리 후에도 `adb devices`에 `IP:포트`가 유지된다.
- [ ] `flutter devices`가 해당 기기를 인식한다.
- [ ] `flutter run -d <device-id>`로 실기기에 앱이 뜬다.
- [ ] `lib/main.dart` 수정 → 핫리로드(`r`)가 즉시 반영된다.
- [ ] `flutter analyze`, `flutter test`가 통과한다.

---

## 참고 링크

- [Flutter 지원 플랫폼 (API 24~37)](https://docs.flutter.dev/reference/supported-platforms)
- [Flutter — Android 개발 환경 설정](https://docs.flutter.dev/platform-integration/android/setup)
- [Android Debug Bridge (adb) — 무선 디버깅](https://developer.android.com/tools/adb)
- [Android Studio 릴리스 노트](https://developer.android.com/studio/releases)
- [Google Play targetSdk 요건](https://support.google.com/googleplay/android-developer/answer/11926878)
- [usbipd-win](https://github.com/dorssel/usbipd-win)

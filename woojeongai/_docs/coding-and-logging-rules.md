# 코딩 규칙 & 로깅

## 코딩 규칙

- **코드만 출력** — 설명·주석 불필요 시 생략
- **수정 범위 엄수** — 지시한 파일·부분만 수정, 임의 리팩터링 금지
- 같은 패턴 파일 수정 시 동일 패턴의 모든 파일을 찾아 일괄 점검·적용
- `dependencies/` 파일: `get_repository` + `get_use_case` 두 함수 **반드시 분리**

## 로깅

- 도메인 흐름: **레이어당 1줄** INFO (동일 요청 10줄 이상 금지)
- 로거 등록: `logging_setup.py`
- `print` 디버그 커밋 금지
- Titanic: `titanic_flow_log` — adapter·usecase·outbound 레이어만 (`ports`는 로그 태그 금지)

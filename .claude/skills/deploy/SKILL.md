---
name: deploy              # 스킬 이름 (슬래시 명령어가 됨, 소문자·숫자·하이픈, 최대 64자)
description: |            # Claude가 자동 판단에 사용하는 설명 (권장)
  프로덕션 배포를 수행합니다.
  배포 전 테스트를 실행하고 체크리스트를 확인합니다.
argument-hint: "[환경]"   # 자동완성 힌트 (예: [이슈번호], [파일명] [형식])
disable-model-invocation: true  # true이면 Claude 자동 실행 금지 (수동 호출만 가능)
user-invocable: false     # false이면 슬래시 메뉴에서 숨김 (Claude만 호출 가능)
allowed-tools:            # 이 스킬 실행 중 승인 없이 허용할 도구
  - Bash
  - Read
model: sonnet             # 이 스킬에 사용할 모델
context: fork             # fork로 설정 시 격리된 서브에이전트로 실행
agent: Explore            # context: fork 시 사용할 에이전트 타입
hooks:                    # 이 스킬 전용 훅
  PostToolUse: []
---
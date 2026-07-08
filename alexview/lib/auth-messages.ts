/** 인증 관련 사용자 메시지 — 프론트·API 라우트에서 동일 문구 사용 */

export const AUTH_MESSAGES = {
  loginFailed: "로그인에 실패했습니다.",
  signupFailed: "회원가입 요청에 실패했습니다.",
  checkIdFailed: "아이디 중복 확인에 실패했습니다.",
  checkNicknameFailed: "닉네임 중복 확인에 실패했습니다.",
  idRequired: "아이디를 입력하세요.",
  nicknameRequired: "닉네임을 입력하세요.",
  idUnavailable: "아이디 중복 확인을 완료해 주세요.",
  nicknameUnavailable: "닉네임 중복 확인을 완료해 주세요.",
  welcome: "환영합니다!",
} as const

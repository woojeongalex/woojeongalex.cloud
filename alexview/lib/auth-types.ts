/** 인증 API 응답 타입 (프론트 공통) */

export type LoginResponse = {
  ok?: boolean
  message?: string
  username?: string | null
  nickname?: string | null
  role?: string
  access_token?: string | null
  refresh_token?: string | null
  token_type?: string | null
}

export type TokenRefreshResponse = {
  access_token: string
  token_type: string
}

export type SignupResponse = {
  ok?: boolean
  message?: string
}

export type SignupFormFields = {
  username: string
  nickname: string
  password: string
  passwordConfirm: string
  email: string
}

export const EMPTY_SIGNUP: SignupFormFields = {
  username: "",
  nickname: "",
  password: "",
  passwordConfirm: "",
  email: "",
}

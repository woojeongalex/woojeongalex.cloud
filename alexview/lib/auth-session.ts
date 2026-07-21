/** 로그인 사용자 정보 + JWT 토큰 — localStorage (클라이언트 전용) */

export type UserSession = {
  username: string
  nickname?: string | null
  role?: string | null
}

const SESSION_KEY = "iuem_user"
const ACCESS_TOKEN_KEY = "iuem_access_token"
const REFRESH_TOKEN_KEY = "iuem_refresh_token"

// ── 유저 세션 ─────────────────────────────────────────────────────────────────

export function getUserSession(): UserSession | null {
  if (typeof window === "undefined") return null
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) return null
    const data = JSON.parse(raw) as UserSession
    if (!data.username) return null
    return data
  } catch {
    return null
  }
}

export function setUserSession(user: UserSession): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify(user))
  window.dispatchEvent(new Event("auth-changed"))
}

export function clearUserSession(): void {
  localStorage.removeItem(SESSION_KEY)
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  window.dispatchEvent(new Event("auth-changed"))
}

/** 인사말에 쓸 표시 이름 (닉네임 우선, 없으면 아이디) */
export function getUserDisplayName(user: UserSession): string {
  return user.nickname?.trim() || user.username.trim()
}

// ── JWT 토큰 ──────────────────────────────────────────────────────────────────

export function setTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

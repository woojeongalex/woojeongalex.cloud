/** 브라우저 → Next /api/auth 호출 */

import { UserFacingError, apiErrorOrFallback } from "@/lib/user-facing-error"
import { getAccessToken, getRefreshToken, setAccessToken } from "@/lib/auth-session"
import type { TokenRefreshResponse } from "@/lib/auth-types"

async function parseJsonResponse<T>(res: Response, fallbackError: string): Promise<T> {
  const raw = await res.text()
  let data = {} as T & { error?: string }
  try {
    if (raw) data = JSON.parse(raw) as T & { error?: string }
  } catch {
    throw new UserFacingError(fallbackError)
  }
  if (!res.ok) {
    throw new UserFacingError(apiErrorOrFallback(data.error, fallbackError))
  }
  return data
}

// 만료 직전 토큰은 가는 동안 만료될 수 있어 조금 일찍 갱신한다(초).
const EXPIRY_SKEW_SEC = 30

/** 토큰 페이로드의 exp 로 만료 여부를 본다. 읽을 수 없으면 만료되지 않은 것으로 둔다(서버가 판단). */
function isExpired(token: string): boolean {
  try {
    const part = token.split(".")[1]
    if (!part) return false
    const json = atob(part.replace(/-/g, "+").replace(/_/g, "/"))
    const exp = (JSON.parse(json) as { exp?: number }).exp
    return typeof exp === "number" && exp - EXPIRY_SKEW_SEC <= Date.now() / 1000
  } catch {
    return false
  }
}

/** refresh 토큰으로 새 access 토큰을 받는다. 실패하면 null. */
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return null
  const refreshRes = await fetch("/api/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
  if (!refreshRes.ok) return null
  const { access_token } = (await refreshRes.json()) as TokenRefreshResponse
  setAccessToken(access_token)
  return access_token
}

/**
 * Authorization: Bearer 헤더를 포함한 인증 fetch.
 *
 * 로그인이 선택인 엔드포인트(노래방·리듬 게임 제출, 랭킹 조회)는 만료된 토큰을 401 이 아니라
 * 비로그인으로 처리한다. 401 만 보고 갱신하면 그런 요청은 조용히 익명으로 저장되므로,
 * 보내기 전에 만료를 직접 확인해 먼저 갱신한다.
 */
export async function authFetch(input: RequestInfo, init: RequestInit = {}): Promise<Response> {
  let token = getAccessToken()
  if (token && isExpired(token)) token = (await refreshAccessToken()) ?? token
  const headers = new Headers(init.headers)
  if (token) headers.set("Authorization", `Bearer ${token}`)
  const res = await fetch(input, { ...init, headers })

  if (res.status !== 401) return res

  // 401 → refresh 시도
  const access_token = await refreshAccessToken()
  if (!access_token) return res

  const retryHeaders = new Headers(init.headers)
  retryHeaders.set("Authorization", `Bearer ${access_token}`)
  return fetch(input, { ...init, headers: retryHeaders })
}

export async function postAuthJson<T>(
  path: string,
  body: unknown,
  fallbackError: string
): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  return parseJsonResponse<T>(res, fallbackError)
}

export async function getAvailability(
  path: string,
  param: string,
  value: string,
  fallbackError: string
): Promise<boolean> {
  const res = await fetch(`${path}?${param}=${encodeURIComponent(value)}`)
  const data = await parseJsonResponse<{ available?: boolean }>(res, fallbackError)
  return Boolean(data.available)
}

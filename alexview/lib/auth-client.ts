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

/** Authorization: Bearer 헤더를 포함한 인증 fetch */
export async function authFetch(input: RequestInfo, init: RequestInit = {}): Promise<Response> {
  const token = getAccessToken()
  const headers = new Headers(init.headers)
  if (token) headers.set("Authorization", `Bearer ${token}`)
  const res = await fetch(input, { ...init, headers })

  if (res.status !== 401) return res

  // 401 → refresh 시도
  const refreshToken = getRefreshToken()
  if (!refreshToken) return res

  const refreshRes = await fetch("/api/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
  if (!refreshRes.ok) return res

  const { access_token } = (await refreshRes.json()) as TokenRefreshResponse
  setAccessToken(access_token)

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

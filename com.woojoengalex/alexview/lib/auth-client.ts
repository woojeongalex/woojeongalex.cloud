/** 브라우저 → Next /api/auth 호출 */

import {
  UserFacingError,
  apiErrorOrFallback,
} from "@/lib/user-facing-error"

async function parseJsonResponse<T>(
  res: Response,
  fallbackError: string
): Promise<T> {
  const raw = await res.text()
  let data = {} as T & { error?: string }
  try {
    if (raw) {
      data = JSON.parse(raw) as T & { error?: string }
    }
  } catch {
    throw new UserFacingError(fallbackError)
  }
  if (!res.ok) {
    throw new UserFacingError(apiErrorOrFallback(data.error, fallbackError))
  }
  return data
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

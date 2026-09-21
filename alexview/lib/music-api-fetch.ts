import { authFetch } from "@/lib/auth-client"
import {
  UserFacingError,
  UI_ERRORS,
  apiErrorOrFallback,
} from "@/lib/user-facing-error"

export async function getMusicJson<T>(path: string): Promise<T> {
  const res = await fetch(path, { cache: "no-store" })
  const data = (await res.json()) as T & { error?: string; detail?: string }
  if (!res.ok) {
    const msg =
      typeof data.detail === "string"
        ? data.detail
        : typeof data.error === "string"
          ? data.error
          : undefined
    throw new UserFacingError(apiErrorOrFallback(msg, UI_ERRORS.requestFailed))
  }
  return data
}

export async function postMusicJson<TBody, TResponse>(
  path: string,
  body: TBody
): Promise<TResponse> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  })
  const data = (await res.json()) as TResponse & { error?: string; detail?: string }
  if (!res.ok) {
    const msg =
      typeof data.detail === "string"
        ? data.detail
        : typeof data.error === "string"
          ? data.error
          : undefined
    throw new UserFacingError(apiErrorOrFallback(msg, UI_ERRORS.requestFailed))
  }
  return data
}

/** multipart/form-data 전송 — Content-Type은 브라우저가 boundary와 함께 설정한다 */
export async function postMusicForm<TResponse>(
  path: string,
  form: FormData
): Promise<TResponse> {
  const res = await fetch(path, { method: "POST", body: form, cache: "no-store" })
  const data = (await res.json()) as TResponse & { error?: string; detail?: string }
  if (!res.ok) {
    const msg =
      typeof data.detail === "string"
        ? data.detail
        : typeof data.error === "string"
          ? data.error
          : undefined
    throw new UserFacingError(apiErrorOrFallback(msg, UI_ERRORS.requestFailed))
  }
  return data
}

/**
 * multipart/form-data 전송 + 인증.
 *
 * 로그인 상태면 authFetch 가 Authorization 헤더를 붙이고 401 시 토큰을
 * 갱신해 재시도한다. 비로그인이면 헤더 없이 그대로 나간다(익명 참여 허용).
 */
export async function postMusicFormAuthed<TResponse>(
  path: string,
  form: FormData
): Promise<TResponse> {
  const res = await authFetch(path, { method: "POST", body: form, cache: "no-store" })
  const data = (await res.json()) as TResponse & { error?: string; detail?: string }
  if (!res.ok) {
    const msg =
      typeof data.detail === "string"
        ? data.detail
        : typeof data.error === "string"
          ? data.error
          : undefined
    throw new UserFacingError(apiErrorOrFallback(msg, UI_ERRORS.requestFailed))
  }
  return data
}

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

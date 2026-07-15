export function getApiBaseUrl(): string {
  const base =
    process.env.API_BASE_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ||
    "http://127.0.0.1:8000"
  return base.replace(/\/$/, "")
}

export async function proxyToBackend(
  path: string,
  init?: RequestInit
): Promise<Response> {
  const url = `${getApiBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`
  return fetch(url, { ...init, cache: "no-store" })
}

/**
 * fetch()는 압축된 업스트림 응답 바디를 투명하게 해제하지만, 원본 Response
 * 객체를 그대로 돌려주면 `content-encoding` 같은 전송 관련 헤더는 그대로
 * 남는다 — 브라우저가 "이미 해제된 바디"를 "압축된 바디"로 오인해
 * ERR_CONTENT_DECODING_FAILED가 난다. 바디를 직접 읽어 새 Response로
 * 감싸고 본문과 무관한 전송 헤더는 버린다.
 */
async function toCleanResponse(res: Response): Promise<Response> {
  const text = await res.text()
  return new Response(text, {
    status: res.status,
    headers: { "Content-Type": res.headers.get("Content-Type") || "application/json" },
  })
}

export async function proxyGet(
  path: string,
  fallbackError: string
): Promise<Response> {
  try {
    return await toCleanResponse(await proxyToBackend(path, { method: "GET" }))
  } catch {
    return new Response(JSON.stringify({ error: fallbackError }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    })
  }
}

export async function proxyPost(
  path: string,
  body: unknown,
  fallbackError: string,
  timeoutMs?: number
): Promise<Response> {
  const controller = timeoutMs ? new AbortController() : undefined
  const timer = controller && timeoutMs
    ? setTimeout(() => controller.abort(), timeoutMs)
    : undefined
  try {
    const res = await proxyToBackend(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller?.signal,
    })
    return await toCleanResponse(res)
  } catch {
    return new Response(JSON.stringify({ error: fallbackError }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    })
  } finally {
    if (timer) clearTimeout(timer)
  }
}

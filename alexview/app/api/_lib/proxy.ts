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

export async function proxyGet(
  path: string,
  fallbackError: string
): Promise<Response> {
  try {
    return await proxyToBackend(path, { method: "GET" })
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
    return res
  } catch {
    return new Response(JSON.stringify({ error: fallbackError }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    })
  } finally {
    if (timer) clearTimeout(timer)
  }
}

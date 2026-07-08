import { NextResponse } from "next/server"
import { proxyGet } from "@/app/api/_lib/proxy"

type CheckConfig = {
  param: string
  backendPath: string
  emptyMessage: string
  fallbackError: string
}

/** check-id / check-nickname 라우트 공통 팩토리 */
export function createCheckRoute(config: CheckConfig) {
  return async function GET(request: Request) {
    const value = new URL(request.url).searchParams.get(config.param)?.trim()
    if (!value) {
      return NextResponse.json({ error: config.emptyMessage }, { status: 400 })
    }
    const query = `${config.backendPath}?${config.param}=${encodeURIComponent(value)}`
    return proxyGet(query, config.fallbackError)
  }
}

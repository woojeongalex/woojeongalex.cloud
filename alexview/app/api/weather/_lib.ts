import { NextResponse } from "next/server"
import { parseFastApiDetail, UI_ERRORS } from "@/lib/user-facing-error"

export const WEATHER_API_BASE =
  process.env.API_BASE_URL?.replace(/\/$/, "") ??
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000"

export function weatherDetailError(
  detail: unknown,
  fallback: string = UI_ERRORS.weatherFailed
) {
  return parseFastApiDetail(detail, fallback)
}

export function weatherProxyFailure(
  fallback: string = UI_ERRORS.weatherFailed,
  status = 503
) {
  return NextResponse.json({ error: fallback }, { status })
}

export function weatherCatchResponse(
  e: unknown,
  fallback: string = UI_ERRORS.weatherFailed
) {
  if (e instanceof Error && e.name === "AbortError") {
    return NextResponse.json(
      { error: "서버 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요." },
      { status: 503 }
    )
  }
  return weatherProxyFailure(fallback)
}

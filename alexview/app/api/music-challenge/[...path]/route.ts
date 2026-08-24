import { NextRequest, NextResponse } from "next/server"
import { getApiBaseUrl } from "@/app/api/_lib/proxy"
import { parseFastApiDetail, UI_ERRORS } from "@/lib/user-facing-error"

export const runtime = "nodejs"

type RouteContext = { params: Promise<{ path: string[] }> }

/**
 * 백엔드 music_challenge 라우터는 `/music_challenge` 프리픽스를 쓰고,
 * 챌린지 생성·제출은 multipart/form-data(오디오·영상 파일)를 받는다.
 * 기존 `/api/music/[...path]` 프록시는 JSON 전용이라 여기서 따로 받는다.
 */
function backendUrl(pathSegments: string[], search: string): string {
  return `${getApiBaseUrl()}/music_challenge/${pathSegments.join("/")}${search}`
}

async function respond(res: Response): Promise<NextResponse> {
  const data = (await res.json().catch(() => null)) as
    | { detail?: unknown; error?: unknown }
    | null

  if (!res.ok) {
    // 502/530 처럼 업스트림이 아예 못 뜬 경우는 "요청 실패"보다 원인이 분명하다.
    const fallback =
      res.status >= 502 ? UI_ERRORS.backendUnavailable : UI_ERRORS.requestFailed
    const message = parseFastApiDetail(data?.detail ?? data?.error, fallback)
    return NextResponse.json({ error: message }, { status: res.status })
  }

  return NextResponse.json(data, { status: res.status })
}

function unavailable(): NextResponse {
  return NextResponse.json(
    { error: UI_ERRORS.backendUnavailable },
    { status: 502 }
  )
}

export async function GET(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  try {
    const res = await fetch(backendUrl(path, request.nextUrl.search), {
      method: "GET",
      cache: "no-store",
    })
    return await respond(res)
  } catch {
    return unavailable()
  }
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  const contentType = request.headers.get("content-type") ?? ""

  try {
    // multipart는 boundary가 들어간 원본 Content-Type을 그대로 넘겨야 하고,
    // 바디도 파싱하지 않고 바이트 그대로 전달한다.
    const body = contentType.includes("multipart/form-data")
      ? await request.arrayBuffer()
      : await request.text()

    const res = await fetch(backendUrl(path, request.nextUrl.search), {
      method: "POST",
      headers: contentType ? { "Content-Type": contentType } : undefined,
      body,
      cache: "no-store",
    })
    return await respond(res)
  } catch {
    return unavailable()
  }
}

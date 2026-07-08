import { NextRequest, NextResponse } from "next/server"
import { proxyToBackend } from "@/app/api/_lib/proxy"

export const runtime = "nodejs"

type RouteContext = { params: Promise<{ path: string[] }> }

async function toSafeJson(res: Response): Promise<unknown> {
  const text = await res.text()
  try {
    return text ? JSON.parse(text) : {}
  } catch {
    return { detail: text || "백엔드 응답을 해석할 수 없습니다." }
  }
}

export async function GET(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  try {
    const query = request.nextUrl.search
    const res = await proxyToBackend(`/titanic/${path.join("/")}${query}`, {
      method: "GET",
      headers: {
        "x-flow-origin": "frontend",
      },
    })
    return NextResponse.json(await toSafeJson(res), { status: res.status })
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "백엔드 서버 연결에 실패했습니다."
    return NextResponse.json({ detail: message }, { status: 502 })
  }
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  try {
    const formData = await request.formData()
    const res = await proxyToBackend(`/titanic/${path.join("/")}`, {
      method: "POST",
      headers: {
        "x-flow-origin": "frontend",
      },
      body: formData,
    })

    return NextResponse.json(await toSafeJson(res), { status: res.status })
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "백엔드 서버 연결에 실패했습니다."
    return NextResponse.json({ detail: message }, { status: 502 })
  }
}

import { NextRequest, NextResponse } from "next/server"
import { proxyToBackend } from "@/app/api/_lib/proxy"

export const runtime = "nodejs"

type RouteContext = { params: Promise<{ path: string[] }> }

async function forward(request: NextRequest, pathSegments: string[]) {
  const path = `/api/music/${pathSegments.join("/")}`
  const search = request.nextUrl.search
  const url = `${path}${search}`

  if (request.method === "GET") {
    const res = await proxyToBackend(url)
    return NextResponse.json(await res.json(), { status: res.status })
  }

  if (request.method === "POST") {
    const body = await request.text()
    const res = await proxyToBackend(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    })
    return NextResponse.json(await res.json(), { status: res.status })
  }

  return NextResponse.json({ error: "허용되지 않은 메서드입니다." }, { status: 405 })
}

export async function GET(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  return forward(request, path)
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  return forward(request, path)
}

import { NextResponse } from "next/server"
import { proxyPost } from "@/app/api/_lib/proxy"

export const runtime = "nodejs"

export async function POST(request: Request) {
  let body: unknown
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: "요청 본문이 올바르지 않습니다." }, { status: 400 })
  }
  return proxyPost("/star-craft/crawler/submit", body, "크롤링에 실패했습니다.", 60_000)
}

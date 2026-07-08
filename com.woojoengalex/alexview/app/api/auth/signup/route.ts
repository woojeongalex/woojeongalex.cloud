import { NextResponse } from "next/server"
import { proxyPost } from "@/app/api/_lib/proxy"
import { AUTH_MESSAGES } from "@/lib/auth-messages"

export const runtime = "nodejs"

export async function POST(request: Request) {
  let body: unknown
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: "요청 본문이 올바르지 않습니다." }, { status: 400 })
  }
  return proxyPost("/api/auth/signup", body, AUTH_MESSAGES.signupFailed, 15_000)
}

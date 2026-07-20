import { NextResponse } from "next/server"

const API = process.env.API_BASE_URL ?? ""

export const runtime = "nodejs"

export async function POST(request: Request) {
  const authHeader = request.headers.get("Authorization") ?? ""
  if (!authHeader.startsWith("Bearer ")) {
    return NextResponse.json({ error: "토큰이 없습니다." }, { status: 401 })
  }
  const res = await fetch(`${API}/api/auth/logout`, {
    method: "POST",
    headers: { Authorization: authHeader },
  })
  if (!res.ok && res.status !== 204) {
    return NextResponse.json({ error: "로그아웃 실패" }, { status: res.status })
  }
  return new NextResponse(null, { status: 204 })
}

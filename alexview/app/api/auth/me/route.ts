import { NextRequest } from "next/server"
import { proxyToBackend } from "@/app/api/_lib/proxy"

export const runtime = "nodejs"

export async function GET(request: NextRequest) {
  const authHeader = request.headers.get("Authorization") ?? ""
  try {
    const res = await proxyToBackend("/api/auth/me", {
      method: "GET",
      headers: { Authorization: authHeader },
    })
    const text = await res.text()
    return new Response(text, {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    })
  } catch {
    return Response.json({ error: "서버 오류" }, { status: 502 })
  }
}

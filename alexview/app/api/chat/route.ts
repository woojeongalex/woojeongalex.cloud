import { NextResponse } from "next/server"
import { generateGeminiText } from "@/lib/gemini-generate"

export const runtime = "nodejs"

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { prompt?: string }
    const prompt = body.prompt?.trim()
    if (!prompt) {
      return NextResponse.json({ error: "메시지가 비어 있습니다." }, { status: 400 })
    }

    const text = await generateGeminiText(prompt)
    return NextResponse.json({ text })
  } catch (error) {
    if (error instanceof Error && error.message === "MISSING_API_KEY") {
      return NextResponse.json({ error: "API 키가 설정되지 않았습니다." }, { status: 500 })
    }
    return NextResponse.json({ error: "서버 오류가 발생했습니다." }, { status: 500 })
  }
}

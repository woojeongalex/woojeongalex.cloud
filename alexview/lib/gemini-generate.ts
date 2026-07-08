import { GoogleGenerativeAI } from "@google/generative-ai"

export async function generateGeminiText(prompt: string): Promise<string> {
  const apiKey = process.env.GEMINI_API_KEY
  if (!apiKey) {
    throw new Error("MISSING_API_KEY")
  }

  const genAI = new GoogleGenerativeAI(apiKey)
  const model = genAI.getGenerativeModel({
    model: process.env.GEMINI_MODEL ?? "gemini-2.0-flash",
  })
  const result = await model.generateContent(prompt)
  return result.response.text()
}

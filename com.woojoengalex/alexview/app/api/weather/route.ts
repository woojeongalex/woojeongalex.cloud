import { readFileSync } from "fs"
import { join } from "path"
import { NextResponse } from "next/server"
import { UI_ERRORS } from "@/lib/user-facing-error"
import {
  WEATHER_API_BASE,
  weatherCatchResponse,
  weatherDetailError,
  weatherProxyFailure,
} from "@/app/api/weather/_lib"

export const runtime = "nodejs"

const BACKEND_FETCH_MS = 1500

function readOpenWeatherKey(): string | null {
  if (process.env.OPENWEATHER_API_KEY?.trim()) {
    return process.env.OPENWEATHER_API_KEY.trim()
  }
  try {
    const envPath = join(process.cwd(), "..", "woojeongai", ".env")
    const content = readFileSync(envPath, "utf8")
    const match = content.match(/^OPENWEATHER_API_KEY=(.+)$/m)
    return match?.[1]?.trim() || null
  } catch {
    return null
  }
}

async function fetchOpenWeatherDirect(apiKey: string) {
  const url = new URL("https://api.openweathermap.org/data/2.5/weather")
  url.searchParams.set("q", "Seoul")
  url.searchParams.set("appid", apiKey)
  url.searchParams.set("units", "metric")
  url.searchParams.set("lang", "kr")

  const res = await fetch(url.toString(), { cache: "no-store" })
  const data = (await res.json()) as {
    main?: { temp?: number }
    weather?: { description?: string }[]
  }

  if (!res.ok) {
    throw new Error("openweather_failed")
  }

  const temp = data.main?.temp
  const description = data.weather?.[0]?.description
  if (temp === undefined || !description) {
    throw new Error("openweather_invalid")
  }

  return { temp: Math.round(temp), description }
}

async function fetchFromBackend() {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), BACKEND_FETCH_MS)

  try {
    const res = await fetch(`${WEATHER_API_BASE}/api/weather`, {
      cache: "no-store",
      signal: controller.signal,
    })
    const data = (await res.json()) as {
      temp?: number
      description?: string
      detail?: unknown
    }

    if (!res.ok) {
      throw new Error(weatherDetailError(data.detail))
    }

    if (data.temp === undefined || !data.description) {
      throw new Error("backend_invalid")
    }

    return { temp: data.temp, description: data.description }
  } finally {
    clearTimeout(timeout)
  }
}

export async function GET() {
  try {
    const weather = await fetchFromBackend()
    return NextResponse.json(weather)
  } catch (backendErr) {
    const apiKey = readOpenWeatherKey()
    if (apiKey) {
      try {
        const weather = await fetchOpenWeatherDirect(apiKey)
        return NextResponse.json(weather)
      } catch {
        return weatherProxyFailure(UI_ERRORS.weatherFailed, 502)
      }
    }

    return weatherCatchResponse(backendErr)
  }
}

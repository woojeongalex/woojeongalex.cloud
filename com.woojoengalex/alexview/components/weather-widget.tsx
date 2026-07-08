"use client"

import { useCallback, useEffect, useState } from "react"
import { CloudSun, Loader2, MapPin, RefreshCw } from "lucide-react"
import { cn } from "@/lib/utils"
import { UserFacingError, UI_ERRORS, apiErrorOrFallback } from "@/lib/user-facing-error"

type WeatherData = {
  temp: number
  description: string
}

type WeatherWidgetProps = {
  variant?: "default" | "compact"
}

export function WeatherWidget({ variant = "default" }: WeatherWidgetProps) {
  const compact = variant === "compact"
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("/api/weather")
      const data = (await res.json()) as WeatherData & { error?: string }
      if (!res.ok) {
        throw new UserFacingError(
          apiErrorOrFallback(data.error, UI_ERRORS.weatherFailed)
        )
      }
      setWeather({ temp: data.temp, description: data.description })
    } catch (e) {
      setWeather(null)
      setError(
        e instanceof UserFacingError ? e.message : UI_ERRORS.weatherFailed
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  return (
    <div
      className={cn(
        "group transition-colors",
        compact
          ? "inline-flex h-9 max-w-[11rem] items-center rounded-lg border border-zinc-300 bg-white px-2 text-zinc-900 shadow-sm sm:max-w-none sm:px-2.5"
          : "block w-full max-w-md rounded-2xl border border-zinc-200 bg-white px-5 py-4 shadow-sm"
      )}
    >
      {loading && (
        <span
          className={cn(
            "flex items-center",
            compact
              ? "justify-center gap-1.5 px-1 text-xs text-zinc-500"
              : "justify-center gap-2 py-3 text-sm text-zinc-500"
          )}
        >
          <Loader2
            className={cn("animate-spin", compact ? "h-3.5 w-3.5" : "h-4 w-4")}
            aria-hidden="true"
          />
          <span className={compact ? "sr-only sm:not-sr-only sm:inline" : undefined}>
            {compact ? "로딩" : "날씨 불러오는 중…"}
          </span>
        </span>
      )}

      {!loading && error && (
        <span
          className={cn(
            "flex items-center",
            compact ? "gap-1 px-0.5 text-xs text-red-600" : "flex-col gap-2 py-2 text-center text-red-600"
          )}
        >
          <span className={compact ? "truncate" : "text-sm"}>
            {compact ? "날씨 오류" : error}
          </span>
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              void load()
            }}
            className={cn(
              "font-medium underline-offset-2 hover:underline",
              compact
                ? "shrink-0 rounded p-0.5 text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                : "text-xs text-zinc-600"
            )}
            aria-label={"다시 시도"}
          >
            {compact ? (
              <RefreshCw className="h-3 w-3" aria-hidden="true" />
            ) : (
              "다시 시도"
            )}
          </button>
        </span>
      )}

      {!loading && weather && compact && (
        <span className="flex min-w-0 items-center gap-1 sm:gap-1.5">
          <MapPin className="hidden h-3 w-3 shrink-0 text-zinc-500 sm:block" aria-hidden="true" />
          <span className="hidden shrink-0 text-[11px] font-medium text-zinc-600 sm:inline">
            Seoul
          </span>
          <CloudSun className="h-3.5 w-3.5 shrink-0 text-amber-500" aria-hidden="true" />
          <span className="shrink-0 text-sm font-semibold tabular-nums text-zinc-950">
            {weather.temp}°
          </span>
          <span className="min-w-0 truncate text-[11px] capitalize text-zinc-600 sm:max-w-[5.5rem] sm:text-xs">
            {weather.description}
          </span>
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              void load()
            }}
            className="ml-0.5 shrink-0 rounded p-0.5 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900"
            aria-label={"날씨 새로고침"}
          >
            <RefreshCw className="h-3 w-3" aria-hidden="true" />
          </button>
        </span>
      )}

      {!loading && weather && !compact && (
        <span className="flex flex-col gap-3">
          <span className="flex items-center justify-between gap-3">
            <span className="flex items-center gap-2 text-sm font-medium text-zinc-500">
              <MapPin className="h-4 w-4 shrink-0" aria-hidden="true" />
              <span>Seoul</span>
            </span>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                void load()
              }}
              className="rounded-lg p-1.5 text-zinc-400 transition-colors hover:bg-zinc-100 hover:text-zinc-700"
              aria-label={"날씨 새로고침"}
            >
              <RefreshCw className="h-4 w-4" aria-hidden="true" />
            </button>
          </span>

          <span className="flex items-center justify-center gap-4 py-1">
            <CloudSun className="h-12 w-12 text-amber-500" aria-hidden="true" />
            <span className="text-center">
              <span className="block text-4xl font-semibold tabular-nums tracking-tight text-zinc-950">
                {weather.temp}°
              </span>
              <span className="mt-1 block text-sm capitalize text-zinc-600">
                {weather.description}
              </span>
            </span>
          </span>
        </span>
      )}
    </div>
  )
}

import { getMusicJson, postMusicJson } from "@/lib/music-api-fetch"

export type InstrumentCatalogHit = {
  instrument_id: string
  label: string
  description: string
  standard_tuning: string
}

export type InstrumentCatalogPayload = {
  query: string
  hits: InstrumentCatalogHit[]
  count: number
}

export async function fetchInstrumentCatalog(
  query = ""
): Promise<InstrumentCatalogPayload> {
  const q = query.trim()
  const data = await getMusicJson<InstrumentCatalogPayload>(
    `/api/music/instrument-catalog?${new URLSearchParams({ q })}`
  )
  return {
    query: data.query ?? q,
    hits: data.hits ?? [],
    count: data.count ?? 0,
  }
}

export type InstrumentEvaluationPayload = {
  instrumentId: "guitar" | "piano"
  tuningAccuracy: number
  pitchDeviationCents: number
  summary: string
  stringReadings: { label: string; cents: number }[]
  fileName: string
  durationSec: number
}

export type InstrumentEvaluationResponse = {
  id: number
  ok: boolean
  message: string
}

export function postInstrumentEvaluation(payload: InstrumentEvaluationPayload) {
  return postMusicJson<InstrumentEvaluationPayload, InstrumentEvaluationResponse>(
    "/api/music/instrument-evaluation",
    payload
  )
}

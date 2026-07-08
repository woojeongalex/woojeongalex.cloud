import { postMusicJson } from "@/lib/music-api-fetch"

export type SingEvaluationPayload = {
  catalogSongId?: string | null
  mrSearchListId?: number | null
  inputSource: "mic" | "video"
  pitchScore: number
  rhythmScore: number
  vocalGrade: string
  summary: string
  fileName: string
  durationSec: number
}

export type SingEvaluationApiResponse = {
  id: number
  ok: boolean
  message: string
}

export function postSingEvaluation(payload: SingEvaluationPayload) {
  return postMusicJson<SingEvaluationPayload, SingEvaluationApiResponse>(
    "/api/music/sing-evaluation",
    payload
  )
}

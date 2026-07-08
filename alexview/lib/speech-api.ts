import { getMusicJson, postMusicJson } from "@/lib/music-api-fetch"

export type SpeechTopicHit = {
  topic_id: string
  label: string
  description: string
}

export type SpeechTopicsPayload = {
  hits: SpeechTopicHit[]
  count: number
}

export async function fetchSpeechTopics(): Promise<SpeechTopicsPayload> {
  const data = await getMusicJson<SpeechTopicsPayload>("/api/music/speech-topics")
  return { hits: data.hits ?? [], count: data.count ?? 0 }
}

export type SpeechEvaluationPayload = {
  topicId: string
  clarityScore: number
  paceScore: number
  toneScore: number
  summary: string
  feedbackPoints: string[]
  fileName: string
  durationSec: number
}

export type SpeechEvaluationResponse = {
  id: number
  ok: boolean
  message: string
}

export function postSpeechEvaluation(payload: SpeechEvaluationPayload) {
  return postMusicJson<SpeechEvaluationPayload, SpeechEvaluationResponse>(
    "/api/music/speech-evaluation",
    payload
  )
}

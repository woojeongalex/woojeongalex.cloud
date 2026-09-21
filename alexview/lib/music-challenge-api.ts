import {
  getMusicJson,
  postMusicForm,
  postMusicFormAuthed,
} from "@/lib/music-api-fetch"

const BASE = "/api/music-challenge"

export type ChallengeType = "vocal" | "instrument" | "both"
export type MediaType = "audio" | "video"

export type Challenge = {
  id: number
  title: string
  description: string
  music_url: string
  challenge_type: ChallengeType
  is_active: boolean
}

export type ChallengesListPayload = {
  items: Challenge[]
  total: number
}

export type Evaluation = {
  id: number
  submission_id: number
  score: number
  feedback: string
  next_challenge_id: number | null
}

export const CHALLENGE_TYPE_LABEL: Record<ChallengeType, string> = {
  vocal: "보컬",
  instrument: "악기",
  both: "보컬 + 악기",
}

export const MEDIA_TYPE_LABEL: Record<MediaType, string> = {
  audio: "음성",
  video: "영상",
}

export async function fetchChallenges(): Promise<ChallengesListPayload> {
  const data = await getMusicJson<ChallengesListPayload>(`${BASE}/challenges`)
  return { items: data.items ?? [], total: data.total ?? 0 }
}

export function fetchChallenge(challengeId: number): Promise<Challenge> {
  return getMusicJson<Challenge>(`${BASE}/challenges/${challengeId}`)
}

/**
 * 사용자 제출 — 영상·음성 업로드 후 AI 평가 결과가 바로 돌아온다.
 *
 * 로그인 상태면 토큰이 함께 나가고 서버가 제출물에 사용자를 기록한다.
 * 비로그인도 참여할 수 있으며 그 경우 기록에는 남지 않는다.
 */
export function submitChallenge(input: {
  challengeId: number
  mediaType: MediaType
  file: File
}): Promise<Evaluation> {
  const form = new FormData()
  form.append("challenge_id", String(input.challengeId))
  form.append("media_type", input.mediaType)
  form.append("media_file", input.file)
  return postMusicFormAuthed<Evaluation>(`${BASE}/submissions/submit`, form)
}

/** 챌린지 생성 — PM(운영자)이 AI 음악을 올릴 때 사용 */
export function createChallenge(input: {
  title: string
  description: string
  challengeType: ChallengeType
  musicFile: File
}): Promise<Challenge> {
  const form = new FormData()
  form.append("title", input.title)
  form.append("description", input.description)
  form.append("challenge_type", input.challengeType)
  form.append("music_file", input.musicFile)
  return postMusicForm<Challenge>(`${BASE}/challenges`, form)
}

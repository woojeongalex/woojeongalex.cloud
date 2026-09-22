import { getMusicJson, getMusicJsonAuthed, postMusicJsonAuthed } from "@/lib/music-api-fetch"
import type { ChartStatus } from "@/lib/music-challenge-api"
import type { RhythmNote, RhythmPress } from "@/lib/rhythm-scoring"

const BASE = "/api/music-challenge"

export type RhythmKeys = 4 | 7
export type RhythmDifficulty = "easy" | "normal" | "hard"

export const RHYTHM_KEYS: RhythmKeys[] = [4, 7]
export const RHYTHM_DIFFICULTIES: RhythmDifficulty[] = ["easy", "normal", "hard"]

export const RHYTHM_DIFFICULTY_LABEL: Record<RhythmDifficulty, string> = {
  easy: "쉬움",
  normal: "보통",
  hard: "어려움",
}

/** 키 배치 — 7키는 오투잼과 같은 S D F Space J K L */
export const RHYTHM_KEY_CODES: Record<RhythmKeys, string[]> = {
  4: ["KeyD", "KeyF", "KeyJ", "KeyK"],
  7: ["KeyS", "KeyD", "KeyF", "Space", "KeyJ", "KeyK", "KeyL"],
}

export const RHYTHM_KEY_LABELS: Record<RhythmKeys, string[]> = {
  4: ["D", "F", "J", "K"],
  7: ["S", "D", "F", "␣", "J", "K", "L"],
}

export type RhythmSheetSummary = {
  keys: RhythmKeys
  difficulty: RhythmDifficulty
  level: number
  note_count: number
}

export type RhythmChart = {
  challenge_id: number
  status: ChartStatus
  bpm: number | null
  duration: number | null
  audio_url: string | null
  sheets: RhythmSheetSummary[]
  error: string | null
}

export type RhythmSheet = {
  challenge_id: number
  keys: RhythmKeys
  difficulty: RhythmDifficulty
  level: number
  bpm: number | null
  duration: number | null
  audio_url: string | null
  notes: RhythmNote[]
}

export type RhythmPlayResult = {
  score: number
  accuracy: number
  max_combo: number
  cool: number
  good: number
  bad: number
  miss: number
  /** 이 채보 랭킹에서 내 최고 기록의 순위. 비로그인이면 null */
  rank: number | null
  best_score: number | null
  is_personal_best: boolean
}

export type RhythmRankingEntry = {
  rank: number
  nickname: string
  score: number
  accuracy: number
  max_combo: number
  achieved_at: string
}

export type RhythmRanking = {
  items: RhythmRankingEntry[]
  me: { rank: number; best_score: number } | null
}

export function fetchRhythmChart(challengeId: number): Promise<RhythmChart> {
  return getMusicJson<RhythmChart>(`${BASE}/challenges/${challengeId}/rhythm`)
}

export function fetchRhythmSheet(
  challengeId: number,
  keys: RhythmKeys,
  difficulty: RhythmDifficulty
): Promise<RhythmSheet> {
  return getMusicJson<RhythmSheet>(
    `${BASE}/challenges/${challengeId}/rhythm/${keys}/${difficulty}`
  )
}

/** 관리자 — 원곡으로 채보 6개를 만든다. 서버는 곧바로 processing 으로 응답한다. */
export function buildRhythmChart(challengeId: number): Promise<RhythmChart> {
  return postMusicJsonAuthed<Record<string, never>, RhythmChart>(
    `${BASE}/challenges/${challengeId}/rhythm/build`,
    {}
  )
}

/** 입력 기록 제출 — 서버가 다시 채점한다. 로그인했을 때만 랭킹에 오른다. */
export function submitRhythmPlay(input: {
  challengeId: number
  keys: RhythmKeys
  difficulty: RhythmDifficulty
  presses: RhythmPress[]
}): Promise<RhythmPlayResult> {
  return postMusicJsonAuthed<{ presses: RhythmPress[] }, RhythmPlayResult>(
    `${BASE}/challenges/${input.challengeId}/rhythm/${input.keys}/${input.difficulty}/plays`,
    { presses: input.presses }
  )
}

export async function fetchRhythmRanking(
  challengeId: number,
  keys: RhythmKeys,
  difficulty: RhythmDifficulty,
  limit = 10
): Promise<RhythmRanking> {
  const data = await getMusicJsonAuthed<RhythmRanking>(
    `${BASE}/challenges/${challengeId}/rhythm/${keys}/${difficulty}/ranking?limit=${limit}`
  )
  return { items: data.items ?? [], me: data.me ?? null }
}

export type RhythmSong = {
  challenge_id: number
  title: string
  bpm: number | null
  duration: number | null
  sheets: RhythmSheetSummary[]
}

/** 리듬 게임 메뉴의 곡 목록 — 채보가 준비된 곡만 */
export async function fetchRhythmSongs(): Promise<RhythmSong[]> {
  const data = await getMusicJson<{ items: RhythmSong[] }>(`${BASE}/rhythm/songs`)
  return data.items ?? []
}

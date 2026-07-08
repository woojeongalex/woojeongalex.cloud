/** 이번 주 스타 — API 연동 전 목업 (곡별 상위 10명) */

export type WeeklyKingEntry = {
  rank: number
  username: string
  pitchScore: number
  rhythmScore: number
}

export type WeeklyKingSlide = {
  id: "vocal" | "instrument"
  categoryLabel: string
  songTitle: string
  songArtist: string
  entries: WeeklyKingEntry[]
}

function totalScore(pitch: number, rhythm: number): number {
  return Math.round((pitch + rhythm) / 2)
}

function buildEntries(
  rows: { username: string; pitch: number; rhythm: number }[]
): WeeklyKingEntry[] {
  return rows.slice(0, 10).map((row, i) => ({
    rank: i + 1,
    username: row.username,
    pitchScore: row.pitch,
    rhythmScore: row.rhythm,
  }))
}

export const WEEKLY_KING_SLIDES: WeeklyKingSlide[] = [
  {
    id: "vocal",
    categoryLabel: "보컬",
    songTitle: "봄날",
    songArtist: "BTS",
    entries: buildEntries([
      { username: "alexlee", pitch: 98, rhythm: 96 },
      { username: "minji_v", pitch: 97, rhythm: 95 },
      { username: "chorus_k", pitch: 96, rhythm: 94 },
      { username: "spring_voice", pitch: 95, rhythm: 93 },
      { username: "iu_fan01", pitch: 94, rhythm: 92 },
      { username: "bts_army", pitch: 93, rhythm: 91 },
      { username: "highnote", pitch: 92, rhythm: 90 },
      { username: "melody_j", pitch: 91, rhythm: 89 },
      { username: "singit", pitch: 90, rhythm: 88 },
      { username: "vocal_lab", pitch: 89, rhythm: 87 },
    ]),
  },
  {
    id: "instrument",
    categoryLabel: "악기",
    songTitle: "Canon in D",
    songArtist: "연습 곡",
    entries: buildEntries([
      { username: "guitar_pro", pitch: 97, rhythm: 95 },
      { username: "piano_keys", pitch: 96, rhythm: 94 },
      { username: "tune_master", pitch: 95, rhythm: 93 },
      { username: "string_wiz", pitch: 94, rhythm: 92 },
      { username: "chord_flow", pitch: 93, rhythm: 91 },
      { username: "ivory_touch", pitch: 92, rhythm: 90 },
      { username: "fret_work", pitch: 91, rhythm: 89 },
      { username: "scale_up", pitch: 90, rhythm: 88 },
      { username: "harmony_k", pitch: 89, rhythm: 87 },
      { username: "pitch_fix", pitch: 88, rhythm: 86 },
    ]),
  },
]

export function entryTotalScore(entry: WeeklyKingEntry): number {
  return totalScore(entry.pitchScore, entry.rhythmScore)
}

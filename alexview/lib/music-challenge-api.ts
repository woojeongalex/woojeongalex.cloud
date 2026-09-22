import {
  getMusicJson,
  getMusicJsonAuthed,
  postMusicFormAuthed,
  putMusicJsonAuthed,
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
  /** 신호 분석 기반 객관 지표. 영상 등 분석 불가 입력이면 null */
  pitch_score: number | null
  rhythm_score: number | null
  tempo: number | null
  /** 노래방·연주 모드로 제출했을 때만 — 서버가 정답 음표와 다시 맞춰 본 결과 */
  karaoke: KaraokeResult | null
}

export type KaraokeResult = {
  score: number
  pitch_accuracy: number
  timing_accuracy: number
  /** 이 곡 랭킹에서 내 최고 기록의 순위. 비로그인이면 null */
  rank: number | null
  /** 이 곡에서 내 최고 점수(이번 포함). 비로그인이면 null */
  best_score: number | null
  is_personal_best: boolean
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
  /**
   * 노래방·연주 모드에서 제출할 때만. 녹음이 곡의 몇 초 지점부터 시작됐는지
   * (기기 지연을 뺀 값). 서버가 이 값으로 녹음을 정답 음표에 맞춰 다시 채점한다.
   */
  karaokeStartOffset?: number
}): Promise<Evaluation> {
  const form = new FormData()
  form.append("challenge_id", String(input.challengeId))
  form.append("media_type", input.mediaType)
  form.append("media_file", input.file)
  if (input.karaokeStartOffset !== undefined) {
    form.append("karaoke_start_offset", input.karaokeStartOffset.toFixed(3))
  }
  return postMusicFormAuthed<Evaluation>(`${BASE}/submissions/submit`, form)
}

/** 챌린지 생성 — 관리자 전용. 서버가 토큰의 role 을 확인한다 */
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
  return postMusicFormAuthed<Challenge>(`${BASE}/challenges`, form)
}

export type HistoryItem = {
  submission_id: number
  challenge_id: number
  challenge_title: string
  challenge_type: ChallengeType
  media_type: MediaType
  created_at: string
  score: number | null
  pitch_score: number | null
  rhythm_score: number | null
}

export type HistoryPayload = {
  items: HistoryItem[]
  total: number
}

/** 내 도전 기록 — 로그인 필수. 최신순으로 돌아온다. */
export async function fetchMyHistory(limit = 30): Promise<HistoryPayload> {
  const data = await getMusicJsonAuthed<HistoryPayload>(
    `${BASE}/submissions/me?limit=${limit}`
  )
  return { items: data.items ?? [], total: data.total ?? 0 }
}

export type ChartStatus = "empty" | "processing" | "ready" | "failed"

/** 정답 멜로디를 어디서 뽑았는지 — 노래면 보컬 스템, 연주곡이면 멜로디 악기 스템 */
export type MelodySource = "vocal" | "instrument"

export type InstrumentKind = "piano" | "guitar" | "violin" | "flute" | "saxophone" | "other"

export const MELODY_SOURCE_LABEL: Record<MelodySource, string> = {
  vocal: "노래 (보컬)",
  instrument: "연주곡 (악기)",
}

export const INSTRUMENT_LABEL: Record<InstrumentKind, string> = {
  piano: "피아노",
  guitar: "기타",
  violin: "바이올린",
  flute: "플루트",
  saxophone: "색소폰",
  other: "기타 악기",
}

/** 정답 멜로디의 음표 하나. 시간은 초, 음높이는 MIDI 번호(60 = 가온 도) */
export type ChartNote = {
  start: number
  end: number
  midi: number
}

/** 가사 한 줄. start 가 null 이면 아직 타이밍을 맞추지 않은 줄 */
export type LyricLine = {
  text: string
  start: number | null
}

export type Chart = {
  challenge_id: number
  status: ChartStatus
  melody_source: MelodySource
  /** 연주곡의 멜로디 악기. 노래면 null */
  instrument: InstrumentKind | null
  notes: ChartNote[]
  duration: number | null
  lyric_lines: LyricLine[]
  /** 도전 화면에서 틀 반주. 없으면 원곡을 대신 쓴다 */
  backing_url: string | null
  has_melody: boolean
  error: string | null
}

export function fetchChart(challengeId: number): Promise<Chart> {
  return getMusicJson<Chart>(`${BASE}/challenges/${challengeId}/chart`)
}

/**
 * 관리자 — 스템 업로드. 서버는 곧바로 processing 상태로 응답하고
 * 정답 멜로디 추출은 뒤에서 한다. 완료 여부는 fetchChart 로 확인한다.
 */
export function uploadStems(input: {
  challengeId: number
  /** 정답을 뽑을 트랙 — 보컬 스템 또는 멜로디 악기 스템 */
  melodyFile: File
  backingFile: File | null
  melodySource: MelodySource
  instrument: InstrumentKind | null
}): Promise<Chart> {
  const form = new FormData()
  form.append("melody_file", input.melodyFile)
  if (input.backingFile) form.append("backing_file", input.backingFile)
  form.append("melody_source", input.melodySource)
  if (input.instrument) form.append("instrument", input.instrument)
  return postMusicFormAuthed<Chart>(
    `${BASE}/challenges/${input.challengeId}/stems`,
    form
  )
}

/** 관리자 — 가사와 줄별 타이밍 저장 */
export function saveLyrics(challengeId: number, lines: LyricLine[]): Promise<Chart> {
  return putMusicJsonAuthed<{ lines: LyricLine[] }, Chart>(
    `${BASE}/challenges/${challengeId}/lyrics`,
    { lines }
  )
}

export type RankingEntry = {
  rank: number
  nickname: string
  score: number
  pitch_accuracy: number | null
  timing_accuracy: number | null
  achieved_at: string
}

export type ChallengeRanking = {
  items: RankingEntry[]
  /** 로그인했고 이 곡 노래방 기록이 있을 때만 */
  me: { rank: number; best_score: number } | null
}

export type WeeklyRankingEntry = RankingEntry & {
  challenge_id: number
  challenge_title: string
}

/**
 * 곡별 노래방·연주 랭킹 — 사람마다 최고 기록 하나.
 * 누구나 볼 수 있고, 로그인했으면 토큰이 붙어 내 순위(me)도 온다.
 */
export async function fetchChallengeRanking(
  challengeId: number,
  limit = 20
): Promise<ChallengeRanking> {
  const data = await getMusicJsonAuthed<ChallengeRanking>(
    `${BASE}/challenges/${challengeId}/ranking?limit=${limit}`
  )
  return { items: data.items ?? [], me: data.me ?? null }
}

/** 이번 주(한국 시간 월요일 0시부터) 사람마다 가장 높은 기록 한 곡 */
export async function fetchWeeklyRanking(limit = 10): Promise<WeeklyRankingEntry[]> {
  const data = await getMusicJson<{ items: WeeklyRankingEntry[] }>(
    `${BASE}/rankings/weekly?limit=${limit}`
  )
  return data.items ?? []
}

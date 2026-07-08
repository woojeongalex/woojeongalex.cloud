import { getMusicJson } from "@/lib/music-api-fetch"

/** FastAPI `GET /api/songs/search` 응답 (Next 프록시 경유) */

export type SongMrHit = {
  /** Neon `song_mr_search_lists.id` (정수 PK) */
  id: number
  catalog_song_id: string
  title: string
  artist: string
  bpm: number
  song_key: string
  range_label: string
  mr_track_name: string
  mr_description: string
}

export type SongMrSearchPayload = {
  query: string
  hits: SongMrHit[]
  count: number
}

export async function fetchSongMrSearch(query: string): Promise<SongMrSearchPayload> {
  const q = query.trim()
  const data = await getMusicJson<SongMrSearchPayload>(
    `/api/songs/search?${new URLSearchParams({ q })}`
  )
  return {
    query: data.query ?? q,
    hits: data.hits ?? [],
    count: data.count ?? 0,
  }
}

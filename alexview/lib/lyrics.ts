import type { LyricLine } from "@/lib/music-challenge-api"

/**
 * Suno 가사의 구간 표시 줄 — `[Verse 1]`, `[Chorus]`, `[Bridge]` 등.
 * 부르는 가사가 아니므로 화면에 띄우지 않는다.
 * `(Ooh)` 같은 괄호 추임새는 실제로 부르는 부분이라 남긴다.
 */
const SECTION_TAG = /^\[[^\]]*\]$/

/** 붙여넣은 가사 텍스트를 화면에 띄울 줄 목록으로 바꾼다. */
export function parseLyricsText(text: string): string[] {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0 && !SECTION_TAG.test(line))
}

/**
 * 가사를 다시 붙여넣었을 때 이미 찍어 둔 타이밍을 최대한 살린다.
 * 같은 자리의 같은 문장이면 시간을 유지하고, 바뀐 줄은 다시 찍게 비운다.
 */
export function mergeLyricTimings(texts: string[], previous: LyricLine[]): LyricLine[] {
  return texts.map((text, i) => ({
    text,
    start: previous[i]?.text === text ? previous[i].start : null,
  }))
}

/** 초를 `1:23.4` 형식으로 */
export function formatSeconds(sec: number | null): string {
  if (sec === null || !Number.isFinite(sec)) return "—"
  const m = Math.floor(sec / 60)
  const s = sec - m * 60
  return `${m}:${s.toFixed(1).padStart(4, "0")}`
}

/** 지금 재생 위치에서 불러야 할 가사 줄. 아직 첫 줄 전이면 -1 */
export function activeLyricIndex(lines: LyricLine[], time: number): number {
  let active = -1
  lines.forEach((line, i) => {
    if (line.start !== null && line.start <= time) active = i
  })
  return active
}

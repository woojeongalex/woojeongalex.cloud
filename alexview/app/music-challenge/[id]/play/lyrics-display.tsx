import { activeLyricIndex } from "@/lib/lyrics"
import type { LyricLine } from "@/lib/music-challenge-api"

// 첫 줄이 이 정도 앞으로 다가오면 미리 보여 준다.
const LEAD_IN_SEC = 3
// 다음 줄 시각을 모르는 마지막 줄은 이만큼 걸려 채운다.
const LAST_LINE_SEC = 4

type LyricsDisplayProps = {
  lines: LyricLine[]
  time: number
}

/** 노래방 가사 — 지금 줄은 부르는 만큼 색이 차오르고, 다음 줄을 흐리게 미리 보여 준다. */
export function LyricsDisplay({ lines, time }: LyricsDisplayProps) {
  const timed = lines.filter((l): l is LyricLine & { start: number } => l.start !== null)
  if (timed.length === 0) return null

  const idx = activeLyricIndex(timed, time)
  const current = idx >= 0 ? timed[idx] : null
  const next = timed[idx + 1] ?? null
  const upcoming = !current && next && next.start - time <= LEAD_IN_SEC ? next : null

  let fill = 0
  if (current) {
    const end = next ? next.start : current.start + LAST_LINE_SEC
    fill = Math.min(1, Math.max(0, (time - current.start) / Math.max(0.1, end - current.start)))
  }

  return (
    <div className="flex min-h-24 flex-col items-center justify-center gap-2 px-4 text-center">
      {current ? (
        // 글자 모양대로 잘라 낸 그라데이션으로 채운다. 덧씌운 span 방식은 긴 줄이
        // 휴대폰에서 두 줄로 넘어가면 어긋난다.
        <p
          className="bg-clip-text text-2xl font-semibold tracking-tight text-transparent sm:text-3xl"
          style={{
            backgroundImage: `linear-gradient(to right, #38bdf8 ${fill * 100}%, rgba(255,255,255,0.35) ${fill * 100}%)`,
          }}
        >
          {current.text}
        </p>
      ) : (
        <p className="text-2xl font-semibold tracking-tight text-white/35 sm:text-3xl">
          {upcoming?.text ?? " "}
        </p>
      )}
      <p className="text-base text-white/40 sm:text-lg">{current ? (next?.text ?? " ") : " "}</p>
    </div>
  )
}

"use client"

import { useEffect, useRef } from "react"
import type { ChartNote } from "@/lib/music-challenge-api"
import { isBlackKey, midiToName } from "@/lib/music-notes"
import { cn } from "@/lib/utils"

const PX_PER_SEC = 40
const ROW_PX = 7
const PAD_SEMITONES = 2

type MelodyPreviewProps = {
  notes: ChartNote[]
  duration: number
  /** 재생 중이면 그 위치에 세로선을 긋고 화면을 따라 움직인다 */
  currentTime?: number
  className?: string
}

/**
 * 추출된 정답 멜로디를 피아노 롤로 보여준다.
 *
 * 관리자가 "제대로 뽑혔는지"를 곡을 들으며 눈으로 확인하는 용도다.
 * 곡 전체를 한 화면에 욱여넣으면 음표 하나하나를 볼 수 없어서,
 * 1초에 40px 로 펼치고 가로로 스크롤하게 했다.
 */
export function MelodyPreview({ notes, duration, currentTime, className }: MelodyPreviewProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = scrollRef.current
    if (!el || currentTime === undefined) return
    const x = currentTime * PX_PER_SEC
    // 재생선이 화면 밖으로 나가려 할 때만 따라간다(사용자가 스크롤해 보는 걸 방해하지 않게).
    if (x < el.scrollLeft || x > el.scrollLeft + el.clientWidth * 0.8) {
      el.scrollLeft = Math.max(0, x - el.clientWidth * 0.2)
    }
  }, [currentTime])

  if (notes.length === 0 || duration <= 0) return null

  const lo = Math.min(...notes.map((n) => n.midi)) - PAD_SEMITONES
  const hi = Math.max(...notes.map((n) => n.midi)) + PAD_SEMITONES
  const rows = hi - lo + 1
  const width = Math.ceil(duration * PX_PER_SEC)
  const height = rows * ROW_PX
  const y = (midi: number) => (hi - midi) * ROW_PX

  return (
    <div className={cn("flex overflow-hidden rounded-2xl border border-border bg-card", className)}>
      {/* 음이름 눈금 — 스크롤해도 왼쪽에 고정 */}
      <div className="relative shrink-0 border-r border-border" style={{ height, width: 36 }}>
        {Array.from({ length: rows }, (_, i) => hi - i)
          .filter((m) => m % 12 === 0)
          .map((m) => (
            <span
              key={m}
              className="absolute right-1 font-mono text-[9px] leading-none text-muted-foreground"
              style={{ top: y(m) }}
            >
              {midiToName(m)}
            </span>
          ))}
      </div>
      <div ref={scrollRef} className="min-w-0 flex-1 overflow-x-auto">
        <svg width={width} height={height} role="img" aria-label={`정답 멜로디 음표 ${notes.length}개`}>
          {Array.from({ length: rows }, (_, i) => hi - i).map((m) =>
            isBlackKey(m) ? (
              <rect key={m} x={0} y={y(m)} width={width} height={ROW_PX} className="fill-muted/60" />
            ) : null
          )}
          {Array.from({ length: Math.floor(duration / 10) + 1 }, (_, i) => i * 10).map((t) => (
            <line
              key={t}
              x1={t * PX_PER_SEC}
              x2={t * PX_PER_SEC}
              y1={0}
              y2={height}
              className="stroke-border"
              strokeWidth={1}
            />
          ))}
          {notes.map((n, i) => (
            <rect
              key={i}
              x={n.start * PX_PER_SEC}
              y={y(n.midi) + 1}
              width={Math.max(2, (n.end - n.start) * PX_PER_SEC - 1)}
              height={ROW_PX - 2}
              rx={2}
              className={cn(
                currentTime !== undefined && currentTime >= n.start && currentTime < n.end
                  ? "fill-sky-500"
                  : "fill-foreground"
              )}
            />
          ))}
          {currentTime !== undefined && (
            <line
              x1={currentTime * PX_PER_SEC}
              x2={currentTime * PX_PER_SEC}
              y1={0}
              y2={height}
              className="stroke-sky-500"
              strokeWidth={2}
            />
          )}
        </svg>
      </div>
    </div>
  )
}

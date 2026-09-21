type ScoreTrendProps = {
  /** 오래된 것부터 최근 순의 0~100 점수 */
  scores: number[]
  className?: string
}

/**
 * 점수 추이 스파크라인.
 *
 * 차트 라이브러리를 쓰지 않은 이유: 보여줄 값이 0~100 한 계열뿐이고,
 * recharts 를 끌어오면 번들만 커진다. 눈금·축 없이 흐름만 보이면 충분하다.
 */
export function ScoreTrend({ scores, className = "mt-3 h-14 w-full" }: ScoreTrendProps) {
  if (scores.length < 2) return null

  const width = 100
  const height = 28
  const step = width / (scores.length - 1)
  const points = scores
    .map((s, i) => {
      const x = i * step
      const y = height - (Math.min(100, Math.max(0, s)) / 100) * height
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(" ")

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="none"
      className={className}
      role="img"
      aria-label={`점수 추이: ${scores.join(", ")}`}
    >
      <polyline
        points={points}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  )
}

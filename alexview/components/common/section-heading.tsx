import { cn } from "@/lib/utils"

type EyebrowBadgeProps = {
  children: React.ReactNode
  className?: string
}

/** 히어로 상단의 점 깜빡이는 알약 라벨. */
export function EyebrowBadge({ children, className }: EyebrowBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-full border border-neon-pink/50 bg-neon-pink/10 px-3.5 py-1 font-orbitron text-[11px] font-bold tracking-[0.2em] text-neon-pink shadow-[0_0_18px_-6px_#ff2e97]",
        className
      )}
    >
      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-neon-pink shadow-[0_0_8px_#ff2e97]" />
      {children}
    </span>
  )
}

type SectionHeadingProps = {
  /** 제목 위의 작은 설명 라벨 */
  label: string
  title: string
  /** 제목 오른쪽에 붙는 보조 영역 (개수, 링크 등) */
  action?: React.ReactNode
}

/** 섹션마다 반복되던 "작은 라벨 + 큰 제목 + 우측 액션" 묶음. */
export function SectionHeading({ label, title, action }: SectionHeadingProps) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p className="font-orbitron text-xs font-bold tracking-[0.25em] text-neon-cyan">{label}</p>
        <h2 className="mt-2 font-display text-3xl tracking-tight text-white sm:text-4xl">{title}</h2>
      </div>
      {action && <div className="flex items-center gap-3">{action}</div>}
    </div>
  )
}

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
        "inline-flex items-center gap-1.5 rounded-full border border-border bg-muted px-3 py-1 text-[11px] font-semibold tracking-wide text-muted-foreground",
        className
      )}
    >
      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-foreground" />
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
        <p className="text-sm font-medium text-muted-foreground">{label}</p>
        <h2 className="mt-2 text-3xl font-semibold tracking-tight">{title}</h2>
      </div>
      {action && <div className="flex items-center gap-3">{action}</div>}
    </div>
  )
}

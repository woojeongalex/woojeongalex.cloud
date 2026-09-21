import { cn } from "@/lib/utils"

type StatusNoteProps = {
  children: React.ReactNode
  className?: string
}

/**
 * 로딩·에러·빈 상태를 알리는 안내 박스.
 *
 * 화면 곳곳에서 같은 모양을 손으로 다시 쓰고 있었고, 그때마다
 * `role="status"` 를 빠뜨릴 여지가 있었다. 한 곳으로 모은다.
 */
export function StatusNote({ children, className }: StatusNoteProps) {
  return (
    <p
      role="status"
      className={cn(
        "rounded-2xl border border-border bg-muted/40 px-5 py-6 text-sm text-muted-foreground",
        className
      )}
    >
      {children}
    </p>
  )
}

type LoadingBlockProps = {
  /** 스크린리더에 읽힐 문구 */
  label: string
  className?: string
}

/** 내용이 아직 없을 때 자리를 잡아주는 스켈레톤. */
export function LoadingBlock({ label, className }: LoadingBlockProps) {
  return (
    <div
      role="status"
      className={cn("animate-pulse rounded-3xl border border-border bg-muted/40", className)}
    >
      <span className="sr-only">{label}</span>
    </div>
  )
}

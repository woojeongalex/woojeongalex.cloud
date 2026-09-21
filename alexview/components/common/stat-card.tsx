type StatCardProps = {
  label: string
  value: string
  /** 값 아래 보조 설명 */
  hint?: string
}

/** 숫자 하나를 크게 보여주는 카드. */
export function StatCard({ label, value, hint }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 font-mono text-2xl font-semibold">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

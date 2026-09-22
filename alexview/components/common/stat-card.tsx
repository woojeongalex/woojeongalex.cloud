type StatCardProps = {
  label: string
  value: string
  /** 값 아래 보조 설명 */
  hint?: string
}

/** 숫자 하나를 크게 보여주는 카드. */
export function StatCard({ label, value, hint }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-[0_0_24px_rgba(255,46,151,0.08)]">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 font-orbitron text-2xl font-semibold text-neon-cyan">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

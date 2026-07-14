import { Check, X, type LucideIcon } from "lucide-react"
import type { ReactNode } from "react"

export type AvailabilityStatus = "idle" | "checking" | "available" | "taken" | "error"

export const btnPrimary =
  "inline-flex w-full items-center justify-center gap-2 rounded-xl bg-zinc-950 px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-zinc-800 disabled:opacity-60"

export function availabilityLabel(
  status: AvailabilityStatus,
  takenText = "이미 사용중"
): { text: string; tone: "success" | "error" | "neutral" } | undefined {
  switch (status) {
    case "checking":
      return { text: "확인 중...", tone: "neutral" }
    case "available":
      return { text: "사용가능", tone: "success" }
    case "taken":
      return { text: takenText, tone: "error" }
    case "error":
      return { text: "확인 실패", tone: "error" }
    default:
      return undefined
  }
}

export function AuthFormShell({ children }: { children: ReactNode }) {
  return <div className="mt-8">{children}</div>
}

export function AuthFormMessage({
  error,
  success,
}: {
  error?: string | null
  success?: string | null
}) {
  return (
    <>
      {error && (
        <p className="flex items-center gap-1.5 text-sm font-semibold text-zinc-900" role="status">
          <X className="h-4 w-4 shrink-0" aria-hidden="true" />
          {error}
        </p>
      )}
      {success && (
        <p className="flex items-center gap-1.5 text-sm font-semibold text-zinc-900" role="status">
          <Check className="h-4 w-4 shrink-0" aria-hidden="true" />
          {success}
        </p>
      )}
    </>
  )
}

export function FormHeader({
  icon: Icon,
  label,
  title,
}: {
  icon: LucideIcon
  label: string
  title: string
}) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-zinc-200 bg-zinc-100">
        <Icon className="h-5 w-5 text-zinc-900" aria-hidden="true" />
      </div>
      <div>
        <p className="text-sm text-zinc-500">{label}</p>
        <h2 className="text-2xl font-semibold">{title}</h2>
      </div>
    </div>
  )
}

type FieldStatus = { text: string; tone: "success" | "error" | "neutral" }

function StatusBadge({ status }: { status?: FieldStatus }) {
  if (!status) return null
  const color = status.tone === "neutral" ? "text-zinc-500" : "text-zinc-900"
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-semibold ${color}`}>
      {status.tone === "success" && <Check className="h-3.5 w-3.5" aria-hidden="true" />}
      {status.tone === "error" && <X className="h-3.5 w-3.5" aria-hidden="true" />}
      {status.text}
    </span>
  )
}

const inputClass =
  "w-full rounded-xl border border-zinc-300 bg-white px-4 py-3 text-sm text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-zinc-950"

export function Field({
  name,
  label,
  type,
  placeholder,
  value,
  onChange,
  status,
  required,
}: {
  name?: string
  label: string
  type: string
  placeholder: string
  value?: string
  onChange?: (value: string) => void
  status?: FieldStatus
  required?: boolean
}) {
  const controlled = value !== undefined && onChange !== undefined
  return (
    <label className="block">
      <span className="mb-2 flex items-center gap-2 text-sm font-medium text-zinc-700">
        <span>{label}</span>
        <StatusBadge status={status} />
      </span>
      <input
        name={name}
        type={type}
        placeholder={placeholder}
        required={required}
        className={inputClass}
        {...(controlled
          ? { value, onChange: (e) => onChange(e.target.value) }
          : { defaultValue: "" })}
      />
    </label>
  )
}

export function FieldWithAction({
  name,
  label,
  type,
  placeholder,
  actionLabel,
  value,
  onChange,
  onAction,
  status,
  required,
}: {
  name?: string
  label: string
  type: string
  placeholder: string
  actionLabel: string
  value: string
  onChange: (value: string) => void
  onAction: () => void
  status?: FieldStatus
  required?: boolean
}) {
  return (
    <label className="block">
      <span className="mb-2 flex items-center gap-2 text-sm font-medium text-zinc-700">
        <span>{label}</span>
        <StatusBadge status={status} />
      </span>
      <div className="flex gap-2">
        <input
          name={name}
          type={type}
          placeholder={placeholder}
          value={value}
          required={required}
          onChange={(e) => onChange(e.target.value)}
          className={`min-w-0 flex-1 ${inputClass}`}
        />
        <button
          type="button"
          onClick={onAction}
          className="shrink-0 rounded-xl border border-zinc-900 bg-white px-4 py-3 text-sm font-medium text-zinc-900 transition-colors hover:bg-zinc-50"
        >
          {actionLabel}
        </button>
      </div>
    </label>
  )
}

import Link from "next/link"
import { ArrowLeft } from "lucide-react"

type PageBackButtonProps = {
  href?: string
  label?: string
}

export function PageBackButton({ href = "/", label = "뒤로가기" }: PageBackButtonProps) {
  return (
    <Link
      href={href}
      className="inline-flex w-fit items-center gap-2 rounded-lg border border-neon-cyan/60 bg-card/60 px-4 py-2 text-sm font-medium text-neon-cyan transition-colors hover:bg-neon-cyan/10"
    >
      <ArrowLeft className="h-4 w-4 shrink-0" aria-hidden="true" />
      {label}
    </Link>
  )
}

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
      className="inline-flex w-fit items-center gap-2 rounded-lg border border-zinc-300 bg-white px-4 py-2 text-sm font-medium text-zinc-900 transition-colors hover:bg-zinc-50"
    >
      <ArrowLeft className="h-4 w-4 shrink-0" aria-hidden="true" />
      {label}
    </Link>
  )
}

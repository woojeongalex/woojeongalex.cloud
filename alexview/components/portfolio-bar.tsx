import { ArrowUpRight, BookText, Boxes, NotebookPen } from "lucide-react"

/**
 * 헤더 위의 얇은 띠 — 포트폴리오로 가는 세 갈래.
 *
 * **고정(sticky)하지 않는다.** 헤더는 이미 고정이라 띠까지 붙이면 화면 위를
 * 두 줄이 차지한다. 처음 들어왔을 때 보이면 되는 것이라 스크롤하면 비켜 준다.
 *
 * 주소는 이 배열에만 둔다.
 */
const LINKS = [
  {
    href: "https://woojeongalex.github.io/woojeongalex.cloud",
    icon: NotebookPen,
    label: "개발 기록",
    hint: "이 서비스를 만들며 막혔던 것",
  },
  {
    href: "https://woojeongalex.github.io/arda-docs",
    icon: BookText,
    label: "팀 프로젝트 기록",
    hint: "채용 관리 시스템 · 내 담당 범위",
  },
  {
    href: "https://seuk.suvisdev.cloud",
    icon: Boxes,
    label: "팀 프로젝트 열기",
    hint: "돌아가는 서비스 (팀 SEUK 운영)",
  },
] as const

export function PortfolioBar() {
  return (
    <div className="border-b border-neon-cyan/25 bg-gradient-to-r from-night-900 via-night-800 to-night-900">
      <div className="mx-auto flex w-full max-w-6xl items-center gap-2 px-3 py-2 sm:gap-3 sm:px-6">
        <span className="hidden shrink-0 items-center gap-1.5 font-orbitron text-[11px] font-bold tracking-[0.2em] text-neon-cyan sm:inline-flex">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-neon-cyan shadow-[0_0_8px_#2ee6ff]" />
          PORTFOLIO
        </span>

        {/* 좁은 화면에서는 줄바꿈 대신 옆으로 민다 — 줄이 늘면 띠가 아니라 블록이 된다 */}
        <ul className="flex min-w-0 flex-1 items-center gap-1.5 overflow-x-auto sm:gap-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {LINKS.map((link) => (
            <li key={link.href} className="shrink-0">
              <a
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                title={link.hint}
                className="group inline-flex items-center gap-1.5 rounded-full border border-neon-cyan/35 bg-night-950/60 px-3 py-1 text-xs font-semibold text-foreground transition-all hover:border-neon-cyan hover:bg-neon-cyan/10 hover:text-white hover:shadow-[0_0_14px_-4px_#2ee6ff] sm:px-3.5 sm:text-[13px]"
              >
                <link.icon
                  className="h-3.5 w-3.5 text-neon-cyan transition-colors"
                  aria-hidden="true"
                />
                {link.label}
                <ArrowUpRight
                  className="h-3.5 w-3.5 text-neon-cyan/60 transition-colors group-hover:text-neon-cyan"
                  aria-hidden="true"
                />
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

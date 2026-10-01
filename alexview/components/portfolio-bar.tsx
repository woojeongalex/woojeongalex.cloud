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
    <div className="border-b border-night-600/50 bg-night-900/60">
      <div className="mx-auto flex w-full max-w-6xl items-center gap-2 px-3 py-1.5 sm:px-6">
        <span className="hidden shrink-0 font-orbitron text-[10px] font-bold tracking-[0.2em] text-neon-cyan sm:inline">
          PORTFOLIO
        </span>

        {/* 좁은 화면에서는 줄바꿈 대신 옆으로 민다 — 줄이 늘면 띠가 아니라 블록이 된다 */}
        <ul className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto sm:gap-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {LINKS.map((link) => (
            <li key={link.href} className="shrink-0">
              <a
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                title={link.hint}
                className="group inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium text-foreground/70 transition-colors hover:bg-white/5 hover:text-white sm:text-xs"
              >
                <link.icon
                  className="h-3.5 w-3.5 text-neon-cyan/70 transition-colors group-hover:text-neon-cyan"
                  aria-hidden="true"
                />
                {link.label}
                <ArrowUpRight
                  className="h-3 w-3 text-foreground/40 transition-colors group-hover:text-neon-cyan"
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

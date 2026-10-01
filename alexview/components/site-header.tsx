"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { ArrowUpRight, ChevronDown, Gamepad2, History, Music4 } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useUserSession } from "@/hooks/use-user-session"
import { getUserDisplayName } from "@/lib/auth-session"
import { cn } from "@/lib/utils"

const navLinkClass =
  "inline-flex shrink-0 items-center justify-center gap-1.5 rounded-full px-3.5 py-2 text-xs font-medium transition-all sm:px-4 sm:text-sm"

const idleLink = "text-foreground/75 hover:bg-white/5 hover:text-foreground"
// 지금 보고 있는 메뉴 — 핑크 네온 테두리
const activeLink =
  "border border-neon-pink text-white shadow-[0_0_16px_-2px_#ff2e97,inset_0_0_12px_-4px_#ff2e97]"

/**
 * 챌린지·리듬 게임 외의 화면들.
 *
 * 챌린지가 이 서비스의 본류인데 드롭다운 안에 다른 메뉴들과 섞여 있어서
 * 처음 온 사람은 열어보기 전까지 존재조차 알 수 없었다. 주요 메뉴를 밖으로
 * 꺼내고 나머지를 여기에 모은다.
 */
const SECONDARY_LINKS = [
  { href: "/analyze", label: "보컬 분석" },
  { href: "/instrument", label: "악기" },
  { href: "/speech", label: "스피치" },
]

/**
 * 밖으로 나가는 포트폴리오 링크. 머리의 띠(`components/portfolio-bar.tsx`)와 같은 곳을
 * 가리킨다 — 띠는 스크롤하면 사라지므로, 어디서든 닿을 자리를 여기 하나 더 둔다.
 * 주소를 바꿀 때 두 파일을 같이 고친다.
 */
const PORTFOLIO_LINKS = [
  { href: "https://woojeongalex.github.io/woojeongalex.cloud", label: "개발 기록" },
  { href: "https://woojeongalex.github.io/arda-docs", label: "팀 프로젝트 기록" },
  { href: "https://seuk.suvisdev.cloud", label: "팀 프로젝트 열기" },
]

export function SiteHeader() {
  const user = useUserSession()
  const pathname = usePathname() ?? "/"
  const isActive = (href: string) => pathname === href || pathname.startsWith(`${href}/`)
  const inChallenge = isActive("/music-challenge") && !isActive("/music-challenge/me")

  return (
    <header className="sticky top-0 z-50 border-b border-night-600/60 bg-night-950/80 backdrop-blur-md">
      <nav className="mx-auto flex w-full max-w-6xl min-w-0 flex-col gap-3 px-3 py-3 sm:px-6 md:flex-row md:items-center md:justify-between md:gap-4 md:py-2.5">
        <div className="flex min-w-0 items-center gap-3">
          <Link
            href="/"
            className="neon-text animate-neon-flicker font-orbitron text-xl font-extrabold tracking-[0.25em] text-white"
          >
            IUEM
          </Link>
          <span className="hidden min-w-0 truncate text-xs tracking-[0.14em] text-muted-foreground sm:inline sm:text-sm">
            오늘, 새로운 나와 이음
          </span>
        </div>

        <div className="flex min-w-0 flex-col gap-2 md:items-end">
          <div className="flex min-w-0 flex-wrap items-center gap-1.5">
            <Link href="/music-challenge" className={cn(navLinkClass, inChallenge ? activeLink : idleLink)}>
              <Music4 className="size-3.5" aria-hidden />
              챌린지
            </Link>
            <Link href="/rhythm" className={cn(navLinkClass, isActive("/rhythm") ? activeLink : idleLink)}>
              <Gamepad2 className="size-3.5" aria-hidden />
              리듬 게임
            </Link>
            {user && (
              <Link
                href="/music-challenge/me"
                className={cn(navLinkClass, isActive("/music-challenge/me") ? activeLink : idleLink)}
              >
                <History className="size-3.5" aria-hidden />
                내 기록
              </Link>
            )}
            <DropdownMenu>
              <DropdownMenuTrigger className={cn(navLinkClass, idleLink, "gap-1 data-[state=open]:bg-white/5")}>
                MENU
                <ChevronDown className="size-3.5 opacity-80" aria-hidden />
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                className="min-w-[10rem] overflow-hidden rounded-xl border border-night-600 bg-night-800 p-1 shadow-[0_12px_40px_-12px_#ff2e97]"
              >
                {SECONDARY_LINKS.map((link) => (
                  <DropdownMenuItem
                    key={link.href}
                    asChild
                    className="rounded-lg px-3 py-2.5 font-medium text-foreground focus:bg-night-600 focus:text-white data-[highlighted]:bg-night-600 data-[highlighted]:text-white"
                  >
                    <Link href={link.href} className="flex w-full cursor-pointer">
                      {link.label}
                    </Link>
                  </DropdownMenuItem>
                ))}

                {/* 포트폴리오 — 머리의 띠는 스크롤하면 사라진다. 어디서든 닿을 자리가 하나는 있어야 한다. */}
                <div className="mt-1 border-t border-night-600 px-3 pb-1 pt-2 font-orbitron text-[10px] font-bold tracking-[0.18em] text-neon-cyan">
                  PORTFOLIO
                </div>
                {PORTFOLIO_LINKS.map((link) => (
                  <DropdownMenuItem
                    key={link.href}
                    asChild
                    className="rounded-lg px-3 py-2.5 font-medium text-foreground focus:bg-night-600 focus:text-white data-[highlighted]:bg-night-600 data-[highlighted]:text-white"
                  >
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex w-full cursor-pointer items-center justify-between gap-2"
                    >
                      {link.label}
                      <ArrowUpRight className="size-3.5 shrink-0 text-neon-cyan/70" aria-hidden />
                    </a>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            {!user && (
              <Link
                href="/auth"
                className={cn(navLinkClass, "glow-button bg-primary font-semibold text-primary-foreground")}
              >
                로그인
              </Link>
            )}
          </div>
          {user && (
            <p className="min-w-0 truncate pl-0.5 text-sm text-muted-foreground md:text-right">
              안녕하세요,{" "}
              <Link
                href="/mypage"
                className="font-semibold text-foreground underline decoration-neon-pink/60 underline-offset-4 hover:text-neon-pink"
              >
                {getUserDisplayName(user)}
              </Link>
              님
            </p>
          )}
        </div>
      </nav>
    </header>
  )
}

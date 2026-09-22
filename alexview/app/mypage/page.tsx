"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { UserRound } from "lucide-react"
import { PageBackButton } from "@/components/page-back-button"
import { useUserSession } from "@/hooks/use-user-session"
import {
  clearUserSession,
  getUserDisplayName,
  getUserSession,
} from "@/lib/auth-session"

const navLinkClass =
  "inline-flex shrink-0 items-center justify-center rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors"

export default function MyPage() {
  const router = useRouter()
  const user = useUserSession()
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    setHydrated(true)
  }, [])

  useEffect(() => {
    if (!hydrated) return
    if (!getUserSession()) router.replace("/auth")
  }, [hydrated, router])

  const handleLogout = () => {
    clearUserSession()
    router.push("/")
  }

  if (!hydrated || !user) {
    return (
      <main className="min-h-[calc(100vh-4rem)] px-4 py-10">
        <p className="text-sm text-muted-foreground">로그인 정보를 확인하는 중…</p>
      </main>
    )
  }

  const displayName = getUserDisplayName(user)

  return (
    <main className="min-h-[calc(100vh-4rem)] px-4 py-10 text-foreground">
      <div className="mx-auto w-full max-w-lg animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both">
        <PageBackButton href="/" label="홈으로" />
        <div className="mt-6 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-neon-pink/50 bg-night-900 shadow-[0_0_16px_-4px_#ff2e97]">
            <UserRound className="h-5 w-5 text-neon-pink" aria-hidden="true" />
          </div>
          <h1 className="neon-text font-display text-3xl text-white">마이페이지</h1>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          안녕하세요, <span className="font-semibold text-neon-cyan">{displayName}</span>님
        </p>

        <section className="mt-8 rounded-2xl border border-border bg-night-850/90 p-6 shadow-[0_0_60px_-24px_#ff2e97] backdrop-blur">
          <dl className="grid gap-4 text-sm">
            <div>
              <dt className="font-orbitron text-xs font-medium tracking-[0.15em] text-muted-foreground">아이디</dt>
              <dd className="mt-1 font-semibold text-white">{user.username}</dd>
            </div>
            {user.nickname?.trim() ? (
              <div>
                <dt className="font-orbitron text-xs font-medium tracking-[0.15em] text-muted-foreground">닉네임</dt>
                <dd className="mt-1 font-semibold text-white">{user.nickname}</dd>
              </div>
            ) : null}
          </dl>
        </section>

        <div className="mt-8">
          <button
            type="button"
            onClick={handleLogout}
            className={`${navLinkClass} glow-button border-primary bg-primary text-primary-foreground`}
          >
            로그아웃
          </button>
        </div>
      </div>
    </main>
  )
}

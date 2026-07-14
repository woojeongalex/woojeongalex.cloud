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
      <main className="min-h-[calc(100vh-4rem)] bg-white px-4 py-10">
        <p className="text-sm text-zinc-500">로그인 정보를 확인하는 중…</p>
      </main>
    )
  }

  const displayName = getUserDisplayName(user)

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-white px-4 py-10 text-zinc-950">
      <div className="mx-auto w-full max-w-lg">
        <PageBackButton href="/" label="홈으로" />
        <div className="mt-6 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-zinc-200 bg-zinc-100">
            <UserRound className="h-5 w-5 text-zinc-900" aria-hidden="true" />
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">마이페이지</h1>
        </div>
        <p className="mt-3 text-sm text-zinc-600">
          안녕하세요, <span className="font-semibold text-zinc-950">{displayName}</span>님
        </p>

        <section className="mt-8 rounded-2xl border border-zinc-200 bg-zinc-50 p-6">
          <dl className="grid gap-4 text-sm">
            <div>
              <dt className="font-medium text-zinc-500">아이디</dt>
              <dd className="mt-1 font-semibold text-zinc-950">{user.username}</dd>
            </div>
            {user.nickname?.trim() ? (
              <div>
                <dt className="font-medium text-zinc-500">닉네임</dt>
                <dd className="mt-1 font-semibold text-zinc-950">{user.nickname}</dd>
              </div>
            ) : null}
          </dl>
        </section>

        <div className="mt-8">
          <button
            type="button"
            onClick={handleLogout}
            className={`${navLinkClass} border-zinc-900 bg-zinc-900 text-white hover:bg-zinc-800`}
          >
            로그아웃
          </button>
        </div>
      </div>
    </main>
  )
}

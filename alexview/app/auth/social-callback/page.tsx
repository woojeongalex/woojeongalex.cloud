use client

import { Suspense, useEffect } from react
import { useRouter, useSearchParams } from next/navigation
import { setTokens, setUserSession } from @/lib/auth-session
import { authFetch } from @/lib/auth-client

function SocialCallbackInner() {
  const router = useRouter()
  const params = useSearchParams()

  useEffect(() => {
    const accessToken = params.get(access_token)
    const refreshToken = params.get(refresh_token)
    const error = params.get(error)

    if (error || !accessToken || !refreshToken) {
      router.replace(/auth)
      return
    }

    setTokens(accessToken, refreshToken)

    authFetch(/api/auth/me)
      .then((res) => res.json())
      .then((data: { username?: string; role?: string }) => {
        if (data.username) {
          setUserSession({ username: data.username, role: data.role })
        }
        router.replace(/)
      })
      .catch(() => router.replace(/))
  }, [params, router])

  return (
    <main className=flex min-h-screen items-center justify-center bg-white>
      <p className=text-sm text-zinc-400>로그인 처리 중...</p>
    </main>
  )
}

export default function SocialCallbackPage() {
  return (
    <Suspense
      fallback={
        <main className=flex min-h-screen items-center justify-center bg-white>
          <p className=text-sm text-zinc-400>로그인 처리 중...</p>
        </main>
      }
    >
      <SocialCallbackInner />
    </Suspense>
  )
}

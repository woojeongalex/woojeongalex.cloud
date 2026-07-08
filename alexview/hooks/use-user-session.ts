import { useEffect, useState } from "react"
import { getUserSession, type UserSession } from "@/lib/auth-session"

/** 헤더 등에서 로그인 사용자 동기화 */
export function useUserSession(): UserSession | null {
  const [user, setUser] = useState<UserSession | null>(null)

  useEffect(() => {
    const sync = () => setUser(getUserSession())
    sync()
    window.addEventListener("storage", sync)
    window.addEventListener("auth-changed", sync)
    return () => {
      window.removeEventListener("storage", sync)
      window.removeEventListener("auth-changed", sync)
    }
  }, [])

  return user
}

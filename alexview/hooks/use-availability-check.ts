import { useCallback, useState } from "react"
import type { AvailabilityStatus } from "@/app/auth/auth-components"
import { getAvailability } from "@/lib/auth-client"

/** 아이디·닉네임 중복 확인 — 상태 + check 함수만 노출 */
export function useAvailabilityCheck(
  path: string,
  param: string,
  fallbackError: string
) {
  const [status, setStatus] = useState<AvailabilityStatus>("idle")

  const check = useCallback(
    async (value: string) => {
      const trimmed = value.trim()
      if (!trimmed) {
        setStatus("idle")
        return
      }
      setStatus("checking")
      try {
        const available = await getAvailability(path, param, trimmed, fallbackError)
        setStatus(available ? "available" : "taken")
      } catch {
        setStatus("error")
      }
    },
    [path, param, fallbackError]
  )

  const reset = useCallback(() => setStatus("idle"), [])

  return { status, check, reset }
}

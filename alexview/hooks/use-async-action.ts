import { useCallback, useState } from "react"
import { toUserFacingMessage } from "@/lib/user-facing-error"

/** 폼 제출용 — loading / error / success 한곳에서 관리 */
export function useAsyncAction() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const clearMessages = useCallback(() => {
    setError(null)
    setSuccess(null)
  }, [])

  const run = useCallback(
    async <T,>(
      task: () => Promise<T>,
      options?: {
        fallbackError?: string
        successMessage?: string | ((result: T) => string)
        onSuccess?: (result: T) => void
      }
    ): Promise<T | null> => {
      clearMessages()
      setLoading(true)
      const fallback = options?.fallbackError ?? "요청에 실패했습니다."
      try {
        const result = await task()
        if (options?.successMessage) {
          setSuccess(
            typeof options.successMessage === "function"
              ? options.successMessage(result)
              : options.successMessage
          )
        }
        options?.onSuccess?.(result)
        return result
      } catch (e) {
        setError(toUserFacingMessage(e, fallback))
        return null
      } finally {
        setLoading(false)
      }
    },
    [clearMessages]
  )

  return { loading, error, success, run, clearMessages, setError, setSuccess }
}

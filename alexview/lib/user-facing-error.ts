/** UI에 노출해도 되는 메시지만 허용 (API 원문·스택·URL·시크릿 차단) */

const BLOCKED =
  /https?:\/\/|localhost|127\.0\.0\.1|API_KEY|GEMINI|traceback|Exception|\.py\b|Unhandled|ECONNREFUSED/i

export class UserFacingError extends Error {
  constructor(message: string) {
    super(message)
    this.name = "UserFacingError"
  }
}

export function apiErrorOrFallback(message: unknown, fallback: string): string {
  if (typeof message !== "string") return fallback
  const trimmed = message.trim()
  if (!trimmed || trimmed.length > 160 || BLOCKED.test(trimmed)) return fallback
  return trimmed
}

/** FastAPI `detail` / `error` → UI·API 응답용 안전 문자열 */
export function parseFastApiDetail(detail: unknown, fallback: string): string {
  if (typeof detail === "string") return apiErrorOrFallback(detail, fallback)
  if (Array.isArray(detail)) {
    const joined = detail
      .map((item) =>
        typeof item === "object" && item !== null && "msg" in item
          ? String((item as { msg: string }).msg)
          : String(item)
      )
      .join(", ")
    return apiErrorOrFallback(joined, fallback)
  }
  return fallback
}

export function toUserFacingMessage(error: unknown, fallback: string): string {
  if (error instanceof UserFacingError) return error.message
  return fallback
}

export const UI_ERRORS = {
  requestFailed: "요청에 실패했습니다.",
  micStartFailed: "녹음을 시작할 수 없습니다. 마이크 권한을 확인해 주세요.",
  mediaAnalysisFailed: "분석에 실패했습니다. 다른 파일로 다시 시도해 주세요.",
  aiCoachingFailed: "AI 코칭 요청에 실패했습니다. 잠시 후 다시 시도해 주세요.",
  geminiFailed: "요청에 실패했습니다. 잠시 후 다시 시도해 주세요.",
  geminiQuota:
    "AI 할당량을 초과했습니다. 잠시 후 다시 시도하거나 사용량을 확인해 주세요.",
  exaoneFailed: "로컬 AI 응답에 실패했습니다. 잠시 후 다시 시도해 주세요.",
  backendUnavailable: "서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.",
  crawlerFailed: "크롤링에 실패했습니다. 잠시 후 다시 시도해 주세요.",
  scraperFailed: "스크래핑에 실패했습니다. 잠시 후 다시 시도해 주세요.",
} as const

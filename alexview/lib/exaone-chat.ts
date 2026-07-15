import { UserFacingError, UI_ERRORS, apiErrorOrFallback } from "@/lib/user-facing-error"

export async function sendExaoneChat(message: string): Promise<string> {
  const res = await fetch("/api/exaone/hendricks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    cache: "no-store",
  })
  const data = (await res.json()) as { reply?: string; error?: string }
  if (!res.ok) {
    throw new UserFacingError(apiErrorOrFallback(data.error, UI_ERRORS.exaoneFailed))
  }
  const reply = data.reply?.trim()
  if (!reply) {
    throw new UserFacingError(UI_ERRORS.exaoneFailed)
  }
  return reply
}

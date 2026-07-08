import { createCheckRoute } from "../_lib/create-check-route"
import { AUTH_MESSAGES } from "@/lib/auth-messages"

export const runtime = "nodejs"

export const GET = createCheckRoute({
  param: "nickname",
  backendPath: "/api/auth/check-nickname",
  emptyMessage: AUTH_MESSAGES.nicknameRequired,
  fallbackError: AUTH_MESSAGES.checkNicknameFailed,
})

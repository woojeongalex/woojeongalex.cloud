import { createCheckRoute } from "../_lib/create-check-route"
import { AUTH_MESSAGES } from "@/lib/auth-messages"

export const runtime = "nodejs"

export const GET = createCheckRoute({
  param: "username",
  backendPath: "/api/auth/check-id",
  emptyMessage: AUTH_MESSAGES.idRequired,
  fallbackError: AUTH_MESSAGES.checkIdFailed,
})

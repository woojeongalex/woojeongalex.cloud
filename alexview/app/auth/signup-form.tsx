"use client"

import { useState } from "react"
import { ArrowRight, UserPlus } from "lucide-react"
import { postAuthJson } from "@/lib/auth-client"
import { AUTH_MESSAGES } from "@/lib/auth-messages"
import { EMPTY_SIGNUP, type SignupFormFields, type SignupResponse } from "@/lib/auth-types"
import { useAsyncAction } from "@/hooks/use-async-action"
import { useAvailabilityCheck } from "@/hooks/use-availability-check"
import {
  AuthFormMessage,
  AuthFormShell,
  availabilityLabel,
  btnPrimary,
  Field,
  FieldWithAction,
  FormHeader,
} from "./auth-components"

export function SignupForm() {
  const [form, setForm] = useState<SignupFormFields>(EMPTY_SIGNUP)
  const { loading, error, success, run, setError } = useAsyncAction()

  const usernameCheck = useAvailabilityCheck(
    "/api/auth/check-id",
    "username",
    AUTH_MESSAGES.checkIdFailed
  )
  const nicknameCheck = useAvailabilityCheck(
    "/api/auth/check-nickname",
    "nickname",
    AUTH_MESSAGES.checkNicknameFailed
  )

  const updateField = (key: keyof SignupFormFields) => (value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    if (key === "username") usernameCheck.reset()
    if (key === "nickname") nicknameCheck.reset()
  }

  const passwordMismatch =
    form.passwordConfirm.length > 0 && form.password !== form.passwordConfirm
  const passwordMatch =
    form.password.length > 0 &&
    form.passwordConfirm.length > 0 &&
    form.password === form.passwordConfirm

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const raw = Object.fromEntries(new FormData(e.currentTarget).entries())
    const password = String(raw.password ?? "")
    const passwordConfirm = String(raw.password_confirm ?? "")

    if (password !== passwordConfirm) return
    if (usernameCheck.status !== "available") {
      setError(AUTH_MESSAGES.idUnavailable)
      return
    }
    if (nicknameCheck.status !== "available") {
      setError(AUTH_MESSAGES.nicknameUnavailable)
      return
    }

    await run(
      () =>
        postAuthJson<SignupResponse>(
          "/api/auth/signup",
          {
            username: String(raw.username ?? "").trim(),
            nickname: String(raw.nickname ?? "").trim(),
            password,
            password_confirm: passwordConfirm,
            email: String(raw.email ?? "").trim(),
          },
          AUTH_MESSAGES.signupFailed
        ),
      {
        fallbackError: AUTH_MESSAGES.signupFailed,
        successMessage: (data) => data.message ?? "회원가입이 완료되었습니다.",
        onSuccess: () => {
          setForm(EMPTY_SIGNUP)
          usernameCheck.reset()
          nicknameCheck.reset()
        },
      }
    )
  }

  return (
    <AuthFormShell>
      <FormHeader icon={UserPlus} label="회원가입" title="새 계정 만들기" />
      <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
        <FieldWithAction
          name="username"
          label="아이디"
          type="text"
          placeholder="아이디를 입력하세요"
          actionLabel="중복 확인"
          value={form.username}
          required
          onChange={updateField("username")}
          onAction={() => usernameCheck.check(form.username)}
          status={availabilityLabel(usernameCheck.status)}
        />
        <FieldWithAction
          name="nickname"
          label="닉네임"
          type="text"
          placeholder="닉네임을 입력하세요"
          actionLabel="중복 확인"
          value={form.nickname}
          required
          onChange={updateField("nickname")}
          onAction={() => nicknameCheck.check(form.nickname)}
          status={availabilityLabel(nicknameCheck.status, "불가능")}
        />
        <Field
          name="password"
          label="비밀번호"
          type="password"
          placeholder="비밀번호를 설정하세요"
          value={form.password}
          required
          onChange={updateField("password")}
        />
        <Field
          name="password_confirm"
          label="비밀번호 확인"
          type="password"
          placeholder="비밀번호를 다시 입력하세요"
          value={form.passwordConfirm}
          required
          onChange={updateField("passwordConfirm")}
          status={
            passwordMismatch
              ? { text: "비밀번호가 다릅니다", tone: "error" }
              : passwordMatch
                ? { text: "일치", tone: "success", icon: "check" }
                : undefined
          }
        />
        <Field
          name="email"
          label="이메일"
          type="email"
          placeholder="you@example.com"
          value={form.email}
          required
          onChange={updateField("email")}
        />
        <AuthFormMessage error={error} success={success} />
        <button type="submit" disabled={loading} className={btnPrimary}>
          {loading ? "가입 중..." : "회원가입하기"}
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </button>
      </form>
    </AuthFormShell>
  )
}

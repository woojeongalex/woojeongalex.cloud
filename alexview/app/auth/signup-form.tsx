"use client"

import { useState } from "react"
import { ArrowRight, ChevronRight, UserPlus } from "lucide-react"
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

type TermsState = { service: boolean; privacy: boolean; marketing: boolean }

function TermsItem({
  label,
  required,
  checked,
  onChange,
  href,
}: {
  label: string
  required: boolean
  checked: boolean
  onChange: (v: boolean) => void
  href?: string
}) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 shrink-0 cursor-pointer accent-zinc-950"
      />
      <span className="flex flex-1 items-center gap-1.5 text-sm text-zinc-700">
        <span className={`text-xs font-semibold ${required ? "text-zinc-950" : "text-zinc-400"}`}>
          [{required ? "필수" : "선택"}]
        </span>
        {label}
      </span>
      {href && (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 text-zinc-400 hover:text-zinc-600"
          aria-label={`${label} 보기`}
        >
          <ChevronRight className="h-4 w-4" />
        </a>
      )}
    </div>
  )
}

function TermsSection({
  terms,
  onChange,
}: {
  terms: TermsState
  onChange: (next: TermsState) => void
}) {
  const allChecked = terms.service && terms.privacy && terms.marketing

  function setAll(v: boolean) {
    onChange({ service: v, privacy: v, marketing: v })
  }
  function setOne(key: keyof TermsState, v: boolean) {
    onChange({ ...terms, [key]: v })
  }

  return (
    <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4 space-y-3">
      <label className="flex cursor-pointer items-center gap-2">
        <input
          type="checkbox"
          checked={allChecked}
          onChange={(e) => setAll(e.target.checked)}
          className="h-4 w-4 shrink-0 cursor-pointer accent-zinc-950"
        />
        <span className="text-sm font-semibold text-zinc-950">전체 동의하기</span>
      </label>
      <div className="border-t border-zinc-200" />
      <TermsItem
        label="서비스 이용약관 동의"
        required
        checked={terms.service}
        onChange={(v) => setOne("service", v)}
      />
      <TermsItem
        label="개인정보 수집 및 이용 동의"
        required
        checked={terms.privacy}
        onChange={(v) => setOne("privacy", v)}
      />
      <TermsItem
        label="마케팅·광고성 정보 수신 동의"
        required={false}
        checked={terms.marketing}
        onChange={(v) => setOne("marketing", v)}
      />
    </div>
  )
}

export function SignupForm() {
  const [form, setForm] = useState<SignupFormFields>(EMPTY_SIGNUP)
  const [terms, setTerms] = useState<TermsState>({ service: false, privacy: false, marketing: false })
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
    if (!terms.service || !terms.privacy) {
      setError("필수 약관에 동의해주세요.")
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
            terms_agreed: true,
            privacy_agreed: true,
            marketing_agreed: terms.marketing,
          },
          AUTH_MESSAGES.signupFailed
        ),
      {
        fallbackError: AUTH_MESSAGES.signupFailed,
        successMessage: (data) => data.message ?? "회원가입이 완료되었습니다.",
        onSuccess: () => {
          setForm(EMPTY_SIGNUP)
          setTerms({ service: false, privacy: false, marketing: false })
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
                ? { text: "일치", tone: "success" }
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
        <TermsSection terms={terms} onChange={setTerms} />
        <AuthFormMessage error={error} success={success} />
        <button type="submit" disabled={loading} className={btnPrimary}>
          {loading ? "가입 중..." : "회원가입하기"}
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </button>
      </form>
    </AuthFormShell>
  )
}

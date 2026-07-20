"use client"

import { useState } from "react"
import Link from "next/link"
import { LoginForm } from "./login-form"
import { SignupForm } from "./signup-form"

type View = "social" | "login" | "signup"
type EmailMode = "login" | "signup"

const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? ""

function KakaoIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 3C6.477 3 2 6.582 2 11c0 2.84 1.657 5.344 4.185 6.897l-.937 3.482a.25.25 0 0 0 .374.271L9.89 19.23C10.58 19.407 11.283 19.5 12 19.5c5.523 0 10-3.582 10-8s-4.477-8-10-8z" />
    </svg>
  )
}

function NaverIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M16.273 12.845L7.376 0H0v24h7.727V11.155L16.624 24H24V0h-7.727z" />
    </svg>
  )
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  )
}

function AppleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
    </svg>
  )
}

function InstagramIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z" />
    </svg>
  )
}

const PROVIDERS = [
  {
    id: "kakao",
    label: "카카오로 계속하기",
    style: { background: "#FEE500", color: "#000000" },
    Icon: KakaoIcon,
  },
  {
    id: "naver",
    label: "네이버로 계속하기",
    style: { background: "#03C75A", color: "#ffffff" },
    Icon: NaverIcon,
  },
  {
    id: "google",
    label: "Google로 계속하기",
    style: { background: "#ffffff", color: "#000000", border: "1px solid #e5e7eb" },
    Icon: GoogleIcon,
  },
  {
    id: "apple",
    label: "Apple로 계속하기",
    style: { background: "#000000", color: "#ffffff" },
    Icon: AppleIcon,
  },
  {
    id: "instagram",
    label: "Instagram으로 계속하기",
    style: {
      background: "linear-gradient(135deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888)",
      color: "#ffffff",
    },
    Icon: InstagramIcon,
  },
] as const

function SocialButtons() {
  return (
    <div className="flex flex-col gap-3">
      {PROVIDERS.map(({ id, label, style, Icon }) => (
        <a
          key={id}
          href={`${API}/auth/${id}`}
          className="inline-flex w-full items-center gap-3 rounded-xl px-5 py-3.5 text-sm font-semibold transition-opacity hover:opacity-90"
          style={style}
        >
          <Icon />
          <span className="flex-1 text-center">{label}</span>
        </a>
      ))}
    </div>
  )
}

function EmailSection({ mode, setView }: { mode: EmailMode; setView: (v: View) => void }) {
  return (
    <div className="rounded-[2rem] border border-zinc-200 bg-white p-6 shadow-sm sm:p-8">
      <div className="flex rounded-2xl border border-zinc-200 bg-zinc-50 p-1">
        {(["login", "signup"] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setView(tab)}
            className={`flex-1 rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
              mode === tab ? "bg-zinc-950 text-white" : "text-zinc-600 hover:bg-zinc-100"
            }`}
          >
            {tab === "login" ? "로그인" : "회원가입"}
          </button>
        ))}
      </div>
      {mode === "login" ? <LoginForm /> : <SignupForm />}
      <button
        type="button"
        onClick={() => setView("social")}
        className="mt-4 w-full text-center text-sm text-zinc-400 hover:text-zinc-600"
      >
        ← 소셜 로그인으로 돌아가기
      </button>
    </div>
  )
}

export default function AuthPage() {
  const [view, setView] = useState<View>("social")

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-white px-4 py-10 text-zinc-950">
      <div className="mx-auto grid w-full max-w-6xl gap-8 lg:grid-cols-[1fr_0.95fr]">
        {/* 왼쪽 브랜딩 */}
        <section className="rounded-[2rem] border border-zinc-200 bg-zinc-950 px-6 py-10 text-white shadow-[0_24px_60px_rgba(0,0,0,0.12)] sm:px-10">
          <p className="text-sm font-medium tracking-[0.18em] text-zinc-400 uppercase">
            Account
          </p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
            로그인하고 나만의
            <br />
            분석 기록을 이어가세요.
          </h1>
          <p className="mt-5 max-w-2xl text-sm leading-7 text-zinc-300 sm:text-base">
            소셜 계정 또는 이메일로 빠르게 시작하세요.
          </p>
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-zinc-800 bg-white/5 p-5">
              <p className="text-sm font-medium text-zinc-400">로그인 후 가능</p>
              <p className="mt-3 text-2xl font-semibold">분석 기록 저장</p>
            </div>
            <div className="rounded-2xl border border-zinc-800 bg-white/5 p-5">
              <p className="text-sm font-medium text-zinc-400">회원가입 후 가능</p>
              <p className="mt-3 text-2xl font-semibold">맞춤 피드백 축적</p>
            </div>
          </div>
        </section>

        {/* 오른쪽: 소셜 로그인 or 이메일 폼 */}
        <section>
          {view === "social" ? (
            <div className="rounded-[2rem] border border-zinc-200 bg-white p-6 shadow-sm sm:p-8">
              <p className="mb-6 text-sm font-medium text-zinc-500">계속하려면 로그인 방법을 선택하세요</p>
              <SocialButtons />
              <div className="mt-6 flex items-center gap-3">
                <div className="h-px flex-1 bg-zinc-200" />
                <span className="text-xs text-zinc-400">또는</span>
                <div className="h-px flex-1 bg-zinc-200" />
              </div>
              <div className="mt-4 flex items-center justify-center gap-4 text-sm text-zinc-500">
                <button
                  type="button"
                  onClick={() => setView("login")}
                  className="hover:text-zinc-900"
                >
                  이메일로 로그인
                </button>
                <span className="text-zinc-300">|</span>
                <button
                  type="button"
                  onClick={() => setView("signup")}
                  className="hover:text-zinc-900"
                >
                  이메일로 가입
                </button>
                <span className="text-zinc-300">|</span>
                <Link href="/" className="hover:text-zinc-900">
                  둘러보기
                </Link>
              </div>
            </div>
          ) : (
            <EmailSection
              mode={view as EmailMode}
              setView={setView}
            />
          )}
        </section>
      </div>
    </main>
  )
}

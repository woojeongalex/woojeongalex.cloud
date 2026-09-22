"use client"

import { useState } from "react"
import Link from "next/link"
import { SynthBackdrop } from "@/components/common/synth-backdrop"
import { LoginForm } from "./login-form"
import { SignupForm } from "./signup-form"

type View = "social" | "login" | "signup"
type EmailMode = "login" | "signup"

const AUTH = process.env.NEXT_PUBLIC_AUTH_BASE_URL ?? ""

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
] as const

function SocialButtons() {
  return (
    <div className="flex flex-col gap-3">
      {PROVIDERS.map(({ id, label, style, Icon }) => (
        <a
          key={id}
          href={`${AUTH}/auth/${id}`}
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

// 오른쪽 카드 — 반투명 밤하늘 위에 은은한 핑크 글로우
const cardClass =
  "rounded-[2rem] border border-border bg-night-850/90 p-6 shadow-[0_0_60px_-20px_#ff2e97] backdrop-blur sm:p-8"

function EmailSection({ mode, setView }: { mode: EmailMode; setView: (v: View) => void }) {
  return (
    <div className={cardClass}>
      <div className="flex rounded-2xl border border-border bg-night-900 p-1">
        {(["login", "signup"] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setView(tab)}
            className={`flex-1 rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
              mode === tab
                ? "bg-primary text-primary-foreground shadow-[0_0_18px_-4px_#ff2e97]"
                : "text-muted-foreground hover:bg-accent hover:text-foreground"
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
        className="mt-4 w-full text-center text-sm text-muted-foreground transition-colors hover:text-neon-cyan"
      >
        ← 소셜 로그인으로 돌아가기
      </button>
    </div>
  )
}

export default function AuthPage() {
  const [view, setView] = useState<View>("social")

  return (
    <main className="min-h-[calc(100vh-4rem)] px-4 py-10 text-foreground">
      <div className="mx-auto grid w-full max-w-6xl gap-8 lg:grid-cols-[1fr_0.95fr]">
        {/* 왼쪽 브랜딩 — 석양과 격자 바닥 위에 네온 타이틀 */}
        <section className="relative overflow-hidden rounded-[2rem] border border-border bg-night-950 text-white shadow-[0_0_60px_-24px_#b44cff]">
          <SynthBackdrop sunSize={260} horizon={0.7} />
          <div className="relative flex h-full flex-col px-6 py-10 sm:px-10">
            <p className="font-orbitron text-xs font-semibold tracking-[0.3em] text-neon-cyan uppercase animate-in fade-in slide-in-from-bottom-4 duration-700">
              Account
            </p>
            <h1
              className="neon-text mt-4 font-display text-4xl leading-[1.15] text-white animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both sm:text-5xl"
              style={{ animationDelay: "120ms" }}
            >
              로그인하고 나만의
              <br />
              분석 기록을 이어가세요.
            </h1>
            <p
              className="mt-5 max-w-2xl text-sm leading-7 text-foreground/85 animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both sm:text-base"
              style={{ animationDelay: "240ms" }}
            >
              소셜 계정 또는 이메일로 빠르게 시작하세요.
            </p>
            <div
              className="mt-8 grid gap-4 pb-24 animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both sm:grid-cols-2 lg:pb-40"
              style={{ animationDelay: "360ms" }}
            >
              <div className="rounded-2xl border border-neon-pink/40 bg-night-900/80 p-5 backdrop-blur">
                <p className="text-sm font-medium text-muted-foreground">로그인 후 가능</p>
                <p className="mt-3 text-2xl font-semibold text-white">분석 기록 저장</p>
              </div>
              <div className="rounded-2xl border border-neon-cyan/40 bg-night-900/80 p-5 backdrop-blur">
                <p className="text-sm font-medium text-muted-foreground">회원가입 후 가능</p>
                <p className="mt-3 text-2xl font-semibold text-white">맞춤 피드백 축적</p>
              </div>
            </div>
          </div>
        </section>

        {/* 오른쪽: 소셜 로그인 or 이메일 폼 */}
        <section
          className="animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both"
          style={{ animationDelay: "200ms" }}
        >
          {view === "social" ? (
            <div className={cardClass}>
              <p className="mb-6 text-sm font-medium text-muted-foreground">계속하려면 로그인 방법을 선택하세요</p>
              <SocialButtons />
              <div className="mt-6 flex items-center gap-3">
                <div className="h-px flex-1 bg-border" />
                <span className="text-xs text-muted-foreground">또는</span>
                <div className="h-px flex-1 bg-border" />
              </div>
              <div className="mt-4 flex items-center justify-center gap-4 text-sm text-muted-foreground">
                <button
                  type="button"
                  onClick={() => setView("login")}
                  className="transition-colors hover:text-neon-cyan"
                >
                  이메일로 로그인
                </button>
                <span className="text-night-500">|</span>
                <button
                  type="button"
                  onClick={() => setView("signup")}
                  className="transition-colors hover:text-neon-cyan"
                >
                  이메일로 가입
                </button>
                <span className="text-night-500">|</span>
                <Link href="/" className="transition-colors hover:text-neon-cyan">
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

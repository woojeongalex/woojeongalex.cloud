"use client"

import { useState } from "react"
import { LoginForm } from "./login-form"
import { SignupForm } from "./signup-form"

type AuthMode = "login" | "signup"

export default function AuthPage() {
  const [mode, setMode] = useState<AuthMode>("login")

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-white px-4 py-10 text-zinc-950">
      <div className="mx-auto grid w-full max-w-6xl gap-8 lg:grid-cols-[1fr_0.95fr]">
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
            이 화면에서는 로그인과 회원가입을 모두 진행할 수 있습니다.
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

        <section className="rounded-[2rem] border border-zinc-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="flex rounded-2xl border border-zinc-200 bg-zinc-50 p-1">
            {(["login", "signup"] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setMode(tab)}
                className={`flex-1 rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
                  mode === tab ? "bg-zinc-950 text-white" : "text-zinc-600 hover:bg-zinc-100"
                }`}
              >
                {tab === "login" ? "로그인" : "회원가입"}
              </button>
            ))}
          </div>
          {mode === "login" ? <LoginForm /> : <SignupForm />}
        </section>
      </div>
    </main>
  )
}

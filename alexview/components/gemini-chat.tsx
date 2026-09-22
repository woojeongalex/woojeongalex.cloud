"use client"

import { useEffect, useRef, useState } from "react"
import { EyeOff, LayoutGrid, Mic, Plus } from "lucide-react"
import { useAsyncAction } from "@/hooks/use-async-action"
import { UserFacingError, UI_ERRORS, apiErrorOrFallback } from "@/lib/user-facing-error"

type ChatMessage = { id: string; role: "user" | "assistant"; content: string }

type GeminiChatProps = {
  /** 홈 히어로 오른쪽: 세로만 확대 */
  layout?: "default" | "sidebar"
}

export function GeminiChat({ layout = "default" }: GeminiChatProps) {
  const isSidebar = layout === "sidebar"
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [modelTier, setModelTier] = useState<"fast" | "pro">("fast")
  const { loading, error, run, setError } = useAsyncAction()
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" })
  }, [messages, loading])

  async function send() {
    const trimmed = input.trim()
    if (!trimmed || loading) return

    setError(null)
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    }
    setMessages((prev) => [...prev, userMsg])
    setInput("")

    await run(
      async () => {
        const res = await fetch("/api/gemini/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: trimmed }),
        })
        const data = (await res.json()) as { reply?: string; error?: string }
        if (!res.ok) {
          const msg = apiErrorOrFallback(data.error, UI_ERRORS.geminiFailed)
          const lower = msg.toLowerCase()
          if (msg.includes("429") || lower.includes("quota") || lower.includes("할당량")) {
            throw new UserFacingError(UI_ERRORS.geminiQuota)
          }
          throw new UserFacingError(msg)
        }
        const reply = data.reply?.trim()
        if (!reply) {
          throw new UserFacingError(UI_ERRORS.geminiFailed)
        }
        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: "assistant", content: reply },
        ])
      },
      { fallbackError: UI_ERRORS.geminiFailed }
    )
  }

  const hasThread = messages.length > 0 || loading

  return (
    <div
      className={`w-full min-w-0 font-sans antialiased ${isSidebar ? "" : "max-w-4xl"}`}
    >
      <div className={isSidebar ? "w-full" : "max-w-2xl"}>
        <p className="font-orbitron text-xs uppercase tracking-[0.25em] text-neon-cyan">Gemini</p>
        <h2
          className={`font-display text-white ${
            isSidebar
              ? "mt-1.5 text-xl sm:text-2xl"
              : "mt-2 text-2xl sm:text-3xl"
          }`}
        >
          가요·뮤지컬 연습, 음정·박자 질문을 Gemini와 나눠 보세요.
        </h2>
      </div>

      <div
        className={`flex flex-col overflow-hidden rounded-2xl border border-border bg-night-900 shadow-[0_0_32px_rgba(255,46,151,0.08)] ${
          isSidebar ? "mt-4 min-h-[22rem] sm:min-h-[25rem]" : "mt-6"
        }`}
      >
        {(hasThread || isSidebar) && (
          <div
            ref={scrollRef}
            className={`space-y-2 overflow-y-auto border-b border-border px-4 py-3 text-sm ${
              isSidebar
                ? "min-h-[11rem] flex-1 max-h-[16rem] sm:min-h-[13rem] sm:max-h-[20rem]"
                : hasThread
                  ? "min-h-48 max-h-80 sm:max-h-96"
                  : "hidden"
            }`}
          >
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <p
                  className={`max-w-[92%] rounded-lg px-3 py-2 leading-relaxed ${
                    m.role === "user"
                      ? "bg-neon-pink/20 text-foreground ring-1 ring-neon-pink/40"
                      : "bg-night-800 text-foreground"
                  }`}
                >
                  {m.content}
                </p>
              </div>
            ))}
            {loading && (
              <p className="text-muted-foreground">응답 작성 중…</p>
            )}
            {isSidebar && !hasThread && (
              <p className="text-center text-muted-foreground">
                연습·음정·박자에 대해 질문을 입력해 보세요.
              </p>
            )}
          </div>
        )}

        <label htmlFor="gemini-input" className="sr-only">
          프롬프트 입력
        </label>
        <textarea
          id="gemini-input"
          rows={isSidebar ? 3 : 4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault()
              void send()
            }
          }}
          placeholder="프롬프트를 입력해 Gemini가 할 수 있는 일을 확인해 보세요."
          className={`w-full resize-none border-0 bg-transparent px-4 text-[15px] leading-relaxed text-foreground placeholder:text-muted-foreground outline-none ring-0 focus:ring-0 ${
            isSidebar ? "pt-3 pb-1.5" : "pt-4 pb-2"
          }`}
          disabled={loading}
        />

        <div className="flex flex-wrap items-center justify-between gap-2 px-3 pb-3 pt-1">
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border bg-night-850 text-muted-foreground transition-colors hover:bg-accent hover:text-neon-cyan"
              aria-label="미리보기 끄기 (준비 중)"
            >
              <EyeOff className="h-4 w-4" aria-hidden="true" />
            </button>
            <button
              type="button"
              className="inline-flex h-9 items-center gap-2 rounded-full border border-neon-cyan/60 bg-transparent px-3 text-xs font-medium text-neon-cyan transition-colors hover:bg-neon-cyan/10"
              aria-label="도구 (준비 중)"
            >
              <LayoutGrid className="h-3.5 w-3.5" aria-hidden="true" />
              도구
            </button>
            <label className="sr-only" htmlFor="gemini-model">
              모델
            </label>
            <select
              id="gemini-model"
              value={modelTier}
              onChange={(e) => setModelTier(e.target.value as "fast" | "pro")}
              className="h-9 cursor-pointer rounded-lg border border-border bg-night-850 px-2.5 text-xs text-foreground outline-none hover:bg-accent"
              disabled={loading}
            >
              <option value="fast">빠른 모델</option>
              <option value="pro">고품질</option>
            </select>
          </div>

          <div className="flex flex-wrap items-center justify-end gap-2">
            <button
              type="button"
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-border bg-night-850 text-muted-foreground transition-colors hover:bg-accent hover:text-neon-cyan"
              aria-label="음성 입력 (준비 중)"
            >
              <Mic className="h-4 w-4" aria-hidden="true" />
            </button>
            <button
              type="button"
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-border bg-night-850 text-muted-foreground transition-colors hover:bg-accent hover:text-neon-cyan"
              aria-label="추가 (준비 중)"
            >
              <Plus className="h-4 w-4" aria-hidden="true" />
            </button>
            <button
              type="button"
              onClick={() => void send()}
              disabled={loading || !input.trim()}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground glow-button transition-colors disabled:cursor-not-allowed disabled:opacity-35"
            >
              실행
              <span className="hidden items-center gap-0.5 text-[11px] font-normal text-primary-foreground sm:inline-flex">
                <kbd className="rounded border border-primary-foreground/40 bg-night-950/30 px-1 py-px font-sans">
                  Enter
                </kbd>
              </span>
            </button>
          </div>
        </div>
      </div>

      {error && (
        <p className="mt-3 text-sm text-foreground" role="status">
          {error}
        </p>
      )}

      <p
        className={`max-w-3xl text-xs leading-relaxed text-muted-foreground ${
          isSidebar ? "mt-2" : "mt-4"
        }`}
      >
        Gemini는 AI이며 오류를 낼 수 있습니다. 민감한 개인 정보는 입력하지 마세요.
      </p>
    </div>
  )
}

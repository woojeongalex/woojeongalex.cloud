"use client"

import { useEffect, useRef, useState } from "react"
import { Cpu, Send } from "lucide-react"
import { useAsyncAction } from "@/hooks/use-async-action"
import { sendExaoneChat } from "@/lib/exaone-chat"
import { UI_ERRORS } from "@/lib/user-facing-error"

type ChatMessage = { id: string; role: "user" | "assistant"; content: string }

export function ExaoneChatBanner() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
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
    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: "user", content: trimmed }
    setMessages((prev) => [...prev, userMsg])
    setInput("")

    await run(
      async () => {
        const reply = await sendExaoneChat(trimmed)
        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: "assistant", content: reply },
        ])
      },
      { fallbackError: UI_ERRORS.exaoneFailed }
    )
  }

  return (
    <div className="w-full min-w-0 rounded-3xl border border-border bg-card p-6 sm:p-8">
      <div className="flex items-center gap-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-muted">
          <Cpu className="h-4.5 w-4.5 text-foreground" aria-hidden="true" />
        </span>
        <div>
          <p className="text-xs font-mono tracking-widest uppercase text-muted-foreground">
            Local AI · EXAONE
          </p>
          <p className="text-sm text-muted-foreground">리처드 헨드릭스와 대화하기</p>
        </div>
      </div>

      <h2 className="mt-4 text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
        자체 서버에서 돌아가는 로컬 AI에게 곡을 추천받아 보세요.
      </h2>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        Gemini와 별개로 우리 GPU에서 직접 구동되는 모델입니다. 답변에 곡 데이터를
        검색해 참고하기 때문에 첫 응답까지 다소 시간이 걸릴 수 있습니다.
      </p>

      <div className="mt-6 flex flex-col overflow-hidden rounded-2xl border border-border bg-background">
        {(messages.length > 0 || loading) && (
          <div
            ref={scrollRef}
            className="min-h-48 max-h-80 space-y-2 overflow-y-auto border-b border-border px-4 py-3 text-sm sm:max-h-96"
          >
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <p
                  className={`max-w-[92%] rounded-lg px-3 py-2 leading-relaxed ${
                    m.role === "user"
                      ? "bg-secondary text-secondary-foreground"
                      : "bg-muted text-foreground"
                  }`}
                >
                  {m.content}
                </p>
              </div>
            ))}
            {loading && (
              <p className="text-muted-foreground">
                곡을 검색하고 답변을 준비하는 중… (최대 몇 분 걸릴 수 있어요)
              </p>
            )}
          </div>
        )}

        <label htmlFor="exaone-input" className="sr-only">
          리처드 헨드릭스에게 메시지 보내기
        </label>
        <div className="flex items-end gap-2 px-3 py-2.5">
          <textarea
            id="exaone-input"
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                void send()
              }
            }}
            placeholder="예: 잔잔한 발라드 추천해줘"
            className="min-h-9 flex-1 resize-none border-0 bg-transparent px-1 py-1.5 text-[15px] leading-relaxed text-foreground placeholder:text-muted-foreground outline-none ring-0 focus:ring-0"
            disabled={loading}
          />
          <button
            type="button"
            onClick={() => void send()}
            disabled={loading || !input.trim()}
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground transition-opacity hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-35"
            aria-label="보내기"
          >
            <Send className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>

      {error && (
        <p className="mt-3 text-sm text-muted-foreground" role="status">
          {error}
        </p>
      )}
    </div>
  )
}

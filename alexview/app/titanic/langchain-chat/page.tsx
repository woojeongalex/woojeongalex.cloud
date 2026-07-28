"use client"

import { KeyboardEvent, useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"

import { useAsyncAction } from "@/hooks/use-async-action"
import { sendExaoneChat } from "@/lib/exaone-chat"
import { UI_ERRORS } from "@/lib/user-facing-error"

type ChatMessage = { role: "user" | "assistant"; text: string }

const WIN_FACE = "#d4d0c8"

const BEVEL_RAISED = {
  boxShadow:
    "inset -1px -1px 0 #404040, inset 1px 1px 0 #ffffff, inset -2px -2px 0 #808080, inset 2px 2px 0 #dfdfdf",
}
const BEVEL_SUNKEN = {
  boxShadow:
    "inset 1px 1px 0 #404040, inset -1px -1px 0 #ffffff, inset 2px 2px 0 #808080, inset -2px -2px 0 #dfdfdf",
}

export default function LangchainRetroChatPage() {
  const router = useRouter()
  const logEndRef = useRef<HTMLDivElement>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", text: "안녕하세요~ 랭체인 LLM이에요! 뭐든 물어보세요 ^^" },
  ])
  const [input, setInput] = useState("")
  const { loading, error, run } = useAsyncAction()

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const send = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput("")
    setMessages((prev) => [...prev, { role: "user", text }])
    await run(() => sendExaoneChat(text), {
      fallbackError: UI_ERRORS.exaoneFailed,
      onSuccess: (reply) => setMessages((prev) => [...prev, { role: "assistant", text: reply }]),
    })
  }

  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      void send()
    }
  }

  return (
    <main
      className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-10"
      style={{ background: "#0A0A0A" }}
    >
      <div
        className="w-full max-w-md select-none"
        style={{ fontFamily: '"Dotum", "Malgun Gothic", sans-serif', background: WIN_FACE, padding: 2, ...BEVEL_RAISED }}
      >
        {/* 타이틀바 */}
        <div
          className="flex items-center justify-between px-2 py-1"
          style={{ background: "linear-gradient(90deg, #0a5bd1, #3f9eff)" }}
        >
          <span className="flex items-center gap-1 text-xs font-bold text-white">💬 대화하기</span>
          <div className="flex items-center gap-1">
            <button type="button" className="h-4 w-4 text-[10px] leading-none text-black" style={{ background: WIN_FACE, ...BEVEL_RAISED }}>
              _
            </button>
            <button type="button" className="h-4 w-4 text-[10px] leading-none text-black" style={{ background: WIN_FACE, ...BEVEL_RAISED }}>
              □
            </button>
            <button
              type="button"
              onClick={() => router.push("/titanic")}
              className="h-4 w-4 text-[10px] leading-none text-black"
              style={{ background: WIN_FACE, ...BEVEL_RAISED }}
            >
              ×
            </button>
          </div>
        </div>

        {/* 메뉴바 */}
        <div className="flex gap-3 px-2 py-1 text-[11px]" style={{ background: WIN_FACE, color: "#1a1a1a" }}>
          <span>파일(<u>F</u>)</span>
          <span>기능(<u>K</u>)</span>
          <span>도구(<u>T</u>)</span>
        </div>

        {/* 본문 */}
        <div className="flex gap-1 p-1" style={{ background: WIN_FACE }}>
          {/* 대화 로그 */}
          <div className="flex min-w-0 flex-1 flex-col">
            <div className="px-2 py-0.5 text-[11px] font-bold" style={{ background: "#ece9d8", ...BEVEL_SUNKEN }}>
              대화상대 : 랭체인 LLM
            </div>
            <div
              className="mt-1 h-56 overflow-y-auto px-2 py-1.5 text-[12px] leading-relaxed"
              style={{ background: "#ffffff", color: "#000000", ...BEVEL_SUNKEN }}
            >
              {messages.map((m, i) => (
                <p key={i} className="mb-1 break-words">
                  <span style={{ color: m.role === "user" ? "#0033cc" : "#cc0000", fontWeight: 700 }}>
                    {m.role === "user" ? "나" : "랭체인 LLM"} :
                  </span>{" "}
                  {m.text}
                </p>
              ))}
              {loading && <p style={{ color: "#888888" }}>랭체인 LLM : 입력 중...</p>}
              {error && <p style={{ color: "#cc0000" }}>{error}</p>}
              <div ref={logEndRef} />
            </div>
          </div>

          {/* 버디 목록 */}
          <div className="flex w-16 flex-col gap-1">
            {["🧑‍✈️", "🚢", "🌙"].map((emoji, i) => (
              <div
                key={i}
                className="flex h-[4.6rem] items-center justify-center text-2xl"
                style={{ background: i === 0 ? "#e8f3d6" : "#dceefb", ...BEVEL_RAISED }}
              >
                <span>{emoji}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 툴바 */}
        <div className="flex gap-1 px-2 py-1" style={{ background: WIN_FACE }}>
          {["😊", "🖼", "📎", "🛠"].map((icon, i) => (
            <button
              key={i}
              type="button"
              className="flex h-6 w-6 items-center justify-center text-xs"
              style={{ background: WIN_FACE, ...BEVEL_RAISED }}
            >
              {icon}
            </button>
          ))}
        </div>

        {/* 입력창 */}
        <div className="flex gap-1 px-2 pb-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            disabled={loading}
            placeholder="메시지를 입력하세요..."
            className="flex-1 px-1.5 py-1 text-[12px] outline-none"
            style={{ background: "#ffffff", color: "#000000", ...BEVEL_SUNKEN }}
          />
          <button
            type="button"
            onClick={() => void send()}
            disabled={loading || !input.trim()}
            className="px-3 text-[12px] font-bold disabled:opacity-50"
            style={{ background: WIN_FACE, ...BEVEL_RAISED }}
          >
            보내기(<u>S</u>)
          </button>
        </div>

        {/* 상태바 */}
        <div
          className="px-2 py-1 text-[10px]"
          style={{ background: WIN_FACE, color: "#555555", borderTop: "1px solid #808080" }}
        >
          Powered by LangChain LLM
        </div>
      </div>
    </main>
  )
}

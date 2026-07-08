"use client"

import Image from "next/image"
import { useRouter } from "next/navigation"
import { ChangeEvent, DragEvent, KeyboardEvent, useEffect, useRef, useState } from "react"

import { useAsyncAction } from "@/hooks/use-async-action"
import { setUploadedFileName, uploadTitanicCsv } from "@/lib/titanic-api"

const ACCENT = "#00FF88"

type ChatMessage = { role: "user" | "assistant"; text: string }

export default function TitanicHomePage() {
  const router = useRouter()
  const inputRef = useRef<HTMLInputElement>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploadedFileName, setUploadedFileNameState] = useState<string | null>(null)
  const { loading, error, run } = useAsyncAction()

  const [chatOpen, setChatOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", text: "나는 에드워드 스미스 선장이오. 타이타닉에 대해 무엇이든 물어보시오." },
  ])
  const [input, setInput] = useState("")
  const [chatLoading, setChatLoading] = useState(false)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || chatLoading) return
    setInput("")
    setMessages((prev) => [...prev, { role: "user", text }])
    setChatLoading(true)
    try {
      const res = await fetch("http://127.0.0.1:8000/titanic/smith/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: text }),
      })
      const data = (await res.json()) as { message?: string; accuracy?: number | null; type?: string; detail?: string; error?: string }
      const accuracyText = data.accuracy != null ? `\n\n📊 정확도: ${(data.accuracy * 100).toFixed(2)}%` : ""
      setMessages((prev) => [...prev, { role: "assistant", text: (data.message ?? data.detail ?? data.error ?? "오류가 발생했습니다.") + accuracyText }])
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", text: "서버 오류가 발생했습니다." }])
    } finally {
      setChatLoading(false)
    }
  }

  const handleChatKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  const handleCsvUpload = async (file: File) => {
    const isCsv =
      file.name.toLowerCase().endsWith(".csv") ||
      file.type === "text/csv" ||
      file.type === "application/vnd.ms-excel"
    if (!isCsv) throw new Error("CSV 파일만 업로드할 수 있습니다.")
    const result = await uploadTitanicCsv(file)
    setUploadedFileName(result.file_name)
    setUploadedFileNameState(result.file_name)
  }

  const handleInputChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    await run(() => handleCsvUpload(file), { fallbackError: "업로드에 실패했습니다." })
    event.target.value = ""
  }

  const handleDrop = async (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)
    const file = event.dataTransfer.files?.[0]
    if (!file) return
    await run(() => handleCsvUpload(file), { fallbackError: "업로드에 실패했습니다." })
  }

  return (
    <main
      className="min-h-[calc(100vh-4rem)] px-4 py-10"
      style={{ background: "#0A0A0A", color: "#e5e7eb" }}
    >
      <div className="mx-auto w-full max-w-4xl space-y-8">
        {/* HERO */}
        <section className="text-center">
          <p className="text-xs font-mono tracking-widest uppercase" style={{ color: ACCENT }}>
            // Titanic AI
          </p>
          <h1 className="mt-3 text-4xl font-semibold text-white sm:text-5xl">타이타닉 홈</h1>
          <p className="mt-3 text-sm sm:text-base" style={{ color: "#9ca3af" }}>
            Titanic CSV를 업로드한 뒤 DB에 저장된 데이터를 상세 페이지에서 확인합니다.
          </p>
        </section>

        {/* 업로드 섹션 */}
        <section className="grid gap-6 md:grid-cols-2">
          <article className="rounded-2xl border p-6" style={{ borderColor: "#1f1f1f", background: "#111111" }}>
            <h2 className="text-xl font-semibold text-white">파일 선택</h2>
            <p className="mt-2 text-sm" style={{ color: "#9ca3af" }}>로컬 CSV 파일을 선택해 업로드합니다.</p>
            <input ref={inputRef} type="file" accept=".csv,text/csv" className="hidden" onChange={handleInputChange} />
            <button
              type="button"
              disabled={loading}
              onClick={() => inputRef.current?.click()}
              className="mt-5 rounded-xl px-5 py-3 text-sm font-medium transition-opacity hover:opacity-80 disabled:opacity-40"
              style={{ background: ACCENT, color: "#0A0A0A" }}
            >
              {loading ? "업로드 중…" : "Titanic CSV 선택하기"}
            </button>
          </article>

          <article className="rounded-2xl border p-6" style={{ borderColor: "#1f1f1f", background: "#111111" }}>
            <h2 className="text-xl font-semibold text-white">드래그 앤 드롭</h2>
            <p className="mt-2 text-sm" style={{ color: "#9ca3af" }}>CSV 파일을 아래 영역에 놓아 업로드합니다.</p>
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              className="mt-5 flex min-h-40 items-center justify-center rounded-xl border-2 border-dashed px-4 text-center text-sm transition-colors"
              style={{
                borderColor: isDragging ? ACCENT : "#2a2a2a",
                background: isDragging ? "#0d1a12" : "#0d0d0d",
                color: isDragging ? ACCENT : "#6b7280",
              }}
            >
              여기에 Titanic CSV 파일을 드래그해서 놓으세요.
            </div>
          </article>
        </section>

        {error && (
          <section
            className="rounded-xl border px-4 py-3 text-sm"
            style={{ borderColor: "#ef444433", background: "#1a0a0a", color: "#f87171" }}
          >
            {error}
          </section>
        )}

        <section className="grid gap-6 md:grid-cols-2">
          {/* 타이타닉 데이터 배너 */}
          <article className="rounded-2xl border p-6" style={{ borderColor: "#1f1f1f", background: "#111111" }}>
            <div className="flex justify-center">
              <Image
                src="/titanic-illustration.svg"
                alt="바다 위를 항해하는 타이타닉 일러스트"
                width={400}
                height={150}
                className="h-auto w-full"
                priority
              />
            </div>
            <div className="mt-4 flex flex-col items-center gap-3">
              <p className="text-sm font-mono" style={{ color: uploadedFileName ? ACCENT : "#6b7280" }}>
                {uploadedFileName ? `✓ 업로드 완료: ${uploadedFileName}` : "CSV 업로드 후 상세 페이지로 이동할 수 있습니다."}
              </p>
              <button
                type="button"
                onClick={() => router.push("/titanic/detail")}
                disabled={!uploadedFileName || loading}
                className="rounded-xl px-5 py-3 text-sm font-medium transition-opacity hover:opacity-80 disabled:opacity-30"
                style={{ background: ACCENT, color: "#0A0A0A" }}
              >
                상세페이지 이동하기
              </button>
            </div>
          </article>

          {/* 스미스 선장 채팅 */}
          <article
            className="flex flex-col rounded-2xl border overflow-hidden"
            style={{ borderColor: "#1f1f1f", background: "#111111" }}
          >
            {!chatOpen ? (
              <div className="flex flex-1 flex-col items-center justify-center p-6 gap-3">
                <div className="flex h-[180px] w-full items-center justify-center">
                  <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg" className="h-full w-auto">
                    <style>{`
                      .sea{fill:#1a3a5c}.wave{fill:none;stroke:#2e6ea6;stroke-width:2;opacity:.5}
                      .hull{fill:#1c1c2e}.stripe{fill:#c8a96e}.coat{fill:#1e3a5f}.coat-dark{fill:#162d4a}
                      .gold{fill:#c8a96e}.face{fill:#f0d0a8}.beard{fill:#e8e0d5}.hair{fill:#d0c8c0}
                      .hat{fill:#1c1c2e}.hat-band{fill:#c8a96e}.eye{fill:#4a3728}.shadow{fill:#d4a880}
                      .anchor{fill:none;stroke:#c8a96e;stroke-width:2;stroke-linecap:round}
                      .bg{fill:#0d2137}.star{fill:#c8d8e8;opacity:.6}
                    `}</style>
                    <rect width="680" height="340" className="bg"/>
                    <circle cx="80" cy="30" r="1.5" className="star"/><circle cx="160" cy="18" r="1" className="star"/>
                    <circle cx="240" cy="28" r="1.5" className="star"/><circle cx="420" cy="15" r="1" className="star"/>
                    <circle cx="530" cy="25" r="1.5" className="star"/><circle cx="610" cy="12" r="1" className="star"/>
                    <circle cx="50" cy="55" r="1" className="star"/><circle cx="620" cy="50" r="1.5" className="star"/>
                    <rect x="0" y="230" width="680" height="110" className="sea"/>
                    <path d="M0 235 Q85 225 170 235 Q255 245 340 235 Q425 225 510 235 Q595 245 680 235" className="wave"/>
                    <path d="M0 248 Q85 238 170 248 Q255 258 340 248 Q425 238 510 248 Q595 258 680 248" className="wave" opacity="0.3"/>
                    <path d="M200 230 L480 230 L460 265 L220 265 Z" className="hull"/>
                    <rect x="220" y="210" width="240" height="22" className="hull"/>
                    <rect x="222" y="213" width="236" height="3" className="stripe"/>
                    <rect x="295" y="170" width="22" height="42" className="coat-dark" rx="2"/>
                    <rect x="363" y="178" width="18" height="34" className="coat-dark" rx="2"/>
                    <rect x="295" y="166" width="22" height="8" rx="2" fill="#2a2a3e"/>
                    <rect x="363" y="174" width="18" height="6" rx="2" fill="#2a2a3e"/>
                    <path d="M290 190 Q290 150 340 148 Q390 150 390 190 L395 230 L285 230 Z" className="coat"/>
                    <path d="M320 155 L310 185 L340 175 Z" className="coat-dark"/>
                    <path d="M360 155 L370 185 L340 175 Z" className="coat-dark"/>
                    <circle cx="340" cy="185" r="3" className="gold"/><circle cx="340" cy="200" r="3" className="gold"/><circle cx="340" cy="215" r="3" className="gold"/>
                    <rect x="285" y="152" width="24" height="8" rx="3" className="gold"/>
                    <rect x="371" y="152" width="24" height="8" rx="3" className="gold"/>
                    <line x1="285" y1="156" x2="270" y2="165" stroke="#c8a96e" strokeWidth="1.5"/>
                    <line x1="395" y1="156" x2="410" y2="165" stroke="#c8a96e" strokeWidth="1.5"/>
                    <path d="M285 160 Q260 175 255 200 L270 203 Q272 183 290 170 Z" className="coat"/>
                    <path d="M395 160 Q420 175 425 200 L410 203 Q408 183 390 170 Z" className="coat"/>
                    <path d="M258 198 Q263 210 272 205" stroke="#c8a96e" strokeWidth="1.5" fill="none"/>
                    <path d="M260 192 Q265 204 274 199" stroke="#c8a96e" strokeWidth="1.5" fill="none"/>
                    <path d="M422 198 Q417 210 408 205" stroke="#c8a96e" strokeWidth="1.5" fill="none"/>
                    <path d="M420 192 Q415 204 406 199" stroke="#c8a96e" strokeWidth="1.5" fill="none"/>
                    <ellipse cx="258" cy="207" rx="9" ry="7" className="face"/>
                    <ellipse cx="422" cy="207" rx="9" ry="7" className="face"/>
                    <rect x="330" y="132" width="20" height="22" rx="4" className="face"/>
                    <path d="M325 148 L315 158 L340 155 L365 158 L355 148 Z" fill="#f0f0ee"/>
                    <ellipse cx="340" cy="110" rx="38" ry="42" className="face"/>
                    <ellipse cx="316" cy="118" rx="12" ry="8" className="shadow" opacity="0.3"/>
                    <ellipse cx="364" cy="118" rx="12" ry="8" className="shadow" opacity="0.3"/>
                    <path d="M308 120 Q310 148 340 152 Q370 148 372 120 Q360 135 340 137 Q320 135 308 120 Z" className="beard"/>
                    <path d="M325 112 Q333 117 340 115 Q347 117 355 112 Q350 120 340 118 Q330 120 325 112 Z" className="beard"/>
                    <path d="M318 95 Q326 91 332 94" stroke="#8a7a6a" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
                    <path d="M348 94 Q354 91 362 95" stroke="#8a7a6a" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
                    <ellipse cx="326" cy="102" rx="7" ry="5" fill="#fff"/>
                    <ellipse cx="354" cy="102" rx="7" ry="5" fill="#fff"/>
                    <circle cx="327" cy="103" r="4" className="eye"/><circle cx="355" cy="103" r="4" className="eye"/>
                    <circle cx="328" cy="102" r="1.5" fill="#fff"/><circle cx="356" cy="102" r="1.5" fill="#fff"/>
                    <path d="M337 105 Q334 114 330 117 Q336 120 340 119 Q344 120 350 117 Q346 114 343 105 Z" className="shadow" opacity="0.4"/>
                    <ellipse cx="302" cy="108" rx="7" ry="10" className="face"/>
                    <ellipse cx="378" cy="108" rx="7" ry="10" className="face"/>
                    <path d="M302 80 Q305 65 320 62 Q340 58 360 62 Q375 65 378 80 Q370 70 340 68 Q310 70 302 80 Z" className="hair"/>
                    <rect x="296" y="64" width="88" height="10" rx="5" className="hat"/>
                    <rect x="306" y="42" width="68" height="28" rx="4" className="hat"/>
                    <rect x="306" y="62" width="68" height="6" className="hat-band"/>
                    <circle cx="340" cy="53" r="8" fill="#1c1c2e" stroke="#c8a96e" strokeWidth="1"/>
                    <path d="M340 47 L340 59 M336 50 Q340 48 344 50 M335 57 Q340 60 345 57" className="anchor" strokeWidth="1.2"/>
                    <circle cx="340" cy="49" r="2" stroke="#c8a96e" strokeWidth="1" fill="none"/>
                    <circle cx="317" cy="173" r="5" className="gold"/>
                    <circle cx="317" cy="173" r="3" fill="#1e3a5f"/>
                    <line x1="317" y1="168" x2="317" y2="165" stroke="#c8a96e" strokeWidth="1.5"/>
                  </svg>
                </div>
                <h2 className="text-lg font-semibold text-white">스미스 선장과의 대화</h2>
                <p className="text-center text-sm" style={{ color: "#9ca3af" }}>타이타닉의 선장 에드워드 스미스와 대화해보세요.</p>
                <button
                  type="button"
                  onClick={() => setChatOpen(true)}
                  className="rounded-xl px-5 py-3 text-sm font-medium transition-opacity hover:opacity-80"
                  style={{ background: ACCENT, color: "#0A0A0A" }}
                >
                  대화 시작하기
                </button>
              </div>
            ) : (
              <div className="flex flex-col h-full">
                <div
                  className="flex items-center justify-between border-b px-4 py-3"
                  style={{ borderColor: "#1f1f1f", background: "#0d0d0d" }}
                >
                  <span className="text-sm font-semibold" style={{ color: ACCENT }}>⚓ 스미스 선장과의 대화</span>
                  <button
                    type="button"
                    onClick={() => setChatOpen(false)}
                    className="text-xs transition-colors"
                    style={{ color: "#6b7280" }}
                  >
                    닫기
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-[220px] max-h-[260px]">
                  {messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                      <div
                        className="max-w-[85%] rounded-2xl px-3 py-2 text-sm leading-relaxed"
                        style={
                          msg.role === "user"
                            ? { background: ACCENT, color: "#0A0A0A", borderRadius: "1rem 1rem 0.25rem 1rem" }
                            : { background: "#1a1a1a", border: "1px solid #2a2a2a", color: "#d1d5db", borderRadius: "1rem 1rem 1rem 0.25rem" }
                        }
                      >
                        {msg.text}
                      </div>
                    </div>
                  ))}
                  {chatLoading && (
                    <div className="flex justify-start">
                      <div
                        className="rounded-2xl px-3 py-2 text-sm font-mono"
                        style={{ background: "#1a1a1a", color: ACCENT }}
                      >
                        ▋
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
                <div className="border-t p-3 flex gap-2" style={{ borderColor: "#1f1f1f" }}>
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleChatKey}
                    placeholder="선장에게 질문하세요…"
                    disabled={chatLoading}
                    className="flex-1 rounded-lg border px-3 py-2 text-sm outline-none"
                    style={{ background: "#0d0d0d", borderColor: "#2a2a2a", color: "#e5e7eb" }}
                  />
                  <button
                    type="button"
                    onClick={sendMessage}
                    disabled={chatLoading || !input.trim()}
                    className="rounded-lg px-3 py-2 text-sm font-medium transition-opacity hover:opacity-80 disabled:opacity-40"
                    style={{ background: ACCENT, color: "#0A0A0A" }}
                  >
                    전송
                  </button>
                </div>
              </div>
            )}
          </article>
        </section>
      </div>
    </main>
  )
}

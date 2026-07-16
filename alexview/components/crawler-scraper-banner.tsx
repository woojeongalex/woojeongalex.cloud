"use client"

import { DragEvent, useEffect, useRef, useState } from "react"
import { Send } from "lucide-react"
import { useAsyncAction } from "@/hooks/use-async-action"
import { commandCrawl, commandScrape } from "@/lib/star-craft-api"
import { UI_ERRORS } from "@/lib/user-facing-error"

const ACCENT = "#FFFFFF"

type PanelMode = "crawler" | "scraper"
type LogMessage = { id: string; role: "user" | "assistant"; content: string }

function CrawlerScraperPanel({
  mode,
  description,
  onSubmit,
}: {
  mode: PanelMode
  description: string
  onSubmit: (website: string, command: string) => Promise<{ count: number; keyword?: string }>
}) {
  const [website, setWebsite] = useState("")
  const [command, setCommand] = useState("")
  const [isDragging, setIsDragging] = useState(false)
  const [messages, setMessages] = useState<LogMessage[]>([])
  const { loading, error, run, setError } = useAsyncAction()
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" })
  }, [messages, loading])

  async function handleSubmit() {
    const url = website.trim()
    const cmd = command.trim()
    if (!url || !cmd || loading) return

    setError(null)
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: `🔗 ${url}\n💬 ${cmd}` },
    ])
    setWebsite("")
    setCommand("")

    await run(
      async () => {
        const { count, keyword } = await onSubmit(url, cmd)
        const noun = mode === "crawler" ? "링크" : "문단"
        const summary = keyword
          ? `✅ "${keyword}" 키워드로 ${noun} ${count}건 발견 (JSONL에 누적 저장됨)`
          : `✅ ${noun} ${count}건 발견 (JSONL에 누적 저장됨)`
        setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "assistant", content: summary }])
      },
      { fallbackError: mode === "crawler" ? UI_ERRORS.crawlerFailed : UI_ERRORS.scraperFailed }
    )
  }

  function handleDrop(e: DragEvent<HTMLInputElement>) {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.getData("text/uri-list") || e.dataTransfer.getData("text/plain")
    if (dropped.trim()) setWebsite(dropped.trim())
  }

  return (
    <div className="p-4">
      <p className="text-sm" style={{ color: "#9ca3af" }}>
        {description}
      </p>

      {(messages.length > 0 || loading) && (
        <div
          ref={scrollRef}
          className="mt-3 min-h-40 max-h-64 space-y-2 overflow-y-auto rounded-lg border p-3 text-sm"
          style={{ borderColor: "#1f1f1f", background: "#0d0d0d" }}
        >
          {messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <p
                className="max-w-[92%] whitespace-pre-wrap rounded-lg px-3 py-2 leading-relaxed"
                style={
                  m.role === "user"
                    ? { background: ACCENT, color: "#0A0A0A" }
                    : { background: "#1a1a1a", border: "1px solid #2a2a2a", color: "#d1d5db" }
                }
              >
                {m.content}
              </p>
            </div>
          ))}
          {loading && (
            <p style={{ color: "#6b7280" }}>
              명령을 이해하고 처리하는 중… (사이트 크기에 따라 시간이 걸릴 수 있어요)
            </p>
          )}
        </div>
      )}

      <div className="mt-3 flex flex-col gap-2">
        <label htmlFor={`${mode}-url`} className="sr-only">
          대상 웹사이트 URL
        </label>
        <input
          id={`${mode}-url`}
          type="text"
          value={website}
          onChange={(e) => setWebsite(e.target.value)}
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragging(true)
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          placeholder="URL 입력 또는 링크를 여기로 드래그"
          disabled={loading}
          className="rounded-lg border bg-transparent px-3 py-2 text-sm outline-none transition-colors"
          style={{ borderColor: isDragging ? ACCENT : "#2a2a2a", color: "#e5e7eb" }}
        />
        <div className="flex items-center gap-2">
          <label htmlFor={`${mode}-command`} className="sr-only">
            자연어 명령
          </label>
          <input
            id={`${mode}-command`}
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault()
                void handleSubmit()
              }
            }}
            placeholder="예: 재즈 관련 내용 찾아줘"
            disabled={loading}
            className="flex-1 rounded-lg border bg-transparent px-3 py-2 text-sm outline-none"
            style={{ borderColor: "#2a2a2a", color: "#e5e7eb" }}
          />
          <button
            type="button"
            onClick={() => void handleSubmit()}
            disabled={loading || !website.trim() || !command.trim()}
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-opacity hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-35"
            style={{ background: ACCENT, color: "#0A0A0A" }}
            aria-label="실행"
          >
            <Send className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>

      {error && (
        <p className="mt-2 text-xs" style={{ color: "#6b7280" }} role="status">
          {error}
        </p>
      )}
    </div>
  )
}

export function CrawlerScraperBanner() {
  const [activeTab, setActiveTab] = useState<PanelMode>("crawler")

  return (
    <div className="overflow-hidden rounded-2xl border" style={{ borderColor: "#1f1f1f", background: "#111111" }}>
      <div className="flex border-b" style={{ borderColor: "#1f1f1f" }}>
        {(["crawler", "scraper"] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className="flex-1 px-4 py-3 text-sm font-medium transition-colors"
            style={
              activeTab === tab
                ? { color: ACCENT, borderBottom: `2px solid ${ACCENT}`, background: "#0d0d0d" }
                : { color: "#6b7280", borderBottom: "2px solid transparent" }
            }
          >
            {tab === "crawler" ? "링크 크롤러" : "본문 스크래퍼"}
          </button>
        ))}
      </div>

      <div style={{ display: activeTab === "crawler" ? "block" : "none" }}>
        <CrawlerScraperPanel
          mode="crawler"
          description="페이지에서 원하는 키워드가 포함된 링크를 찾습니다. URL과 키워드는 Redis에 저장되고, 결과는 crawled 폴더에 JSONL로 누적됩니다."
          onSubmit={async (website, command) => {
            const { count, results } = await commandCrawl(website, command)
            return { count, keyword: results[0]?.keyword }
          }}
        />
      </div>
      <div style={{ display: activeTab === "scraper" ? "block" : "none" }}>
        <CrawlerScraperPanel
          mode="scraper"
          description="페이지 본문에서 원하는 키워드가 포함된 문단을 추출합니다. URL과 키워드는 Redis에 저장되고, 결과는 scraped 폴더에 JSONL로 누적됩니다."
          onSubmit={async (website, command) => {
            const { count, results } = await commandScrape(website, command)
            return { count, keyword: results[0]?.keyword }
          }}
        />
      </div>
    </div>
  )
}

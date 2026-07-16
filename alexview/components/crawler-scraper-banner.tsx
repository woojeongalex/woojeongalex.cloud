"use client"

import { DragEvent, useEffect, useRef, useState } from "react"
import { Bot, Send } from "lucide-react"
import { useAsyncAction } from "@/hooks/use-async-action"
import { commandCrawl, commandScrape } from "@/lib/star-craft-api"
import { UI_ERRORS } from "@/lib/user-facing-error"

type PanelMode = "crawler" | "scraper"
type LogMessage = { id: string; role: "user" | "assistant"; content: string }

function CrawlerScraperPanel({
  mode,
  title,
  description,
  onSubmit,
}: {
  mode: PanelMode
  title: string
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
    <div className="flex flex-col overflow-hidden rounded-2xl border border-border bg-background">
      <div className="border-b border-border px-4 py-3">
        <p className="text-xs font-mono tracking-widest uppercase text-muted-foreground">
          {mode === "crawler" ? "Crawler" : "Scraper"}
        </p>
        <p className="text-sm font-medium text-foreground">{title}</p>
        <p className="mt-1 text-xs text-muted-foreground">{description}</p>
      </div>

      {(messages.length > 0 || loading) && (
        <div
          ref={scrollRef}
          className="min-h-40 max-h-64 space-y-2 overflow-y-auto border-b border-border px-4 py-3 text-sm"
        >
          {messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <p
                className={`max-w-[92%] whitespace-pre-wrap rounded-lg px-3 py-2 leading-relaxed ${
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
              명령을 이해하고 처리하는 중… (사이트 크기에 따라 시간이 걸릴 수 있어요)
            </p>
          )}
        </div>
      )}

      <div className="flex flex-col gap-2 p-3">
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
          className={`rounded-lg border bg-transparent px-3 py-2 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground ${
            isDragging ? "border-foreground" : "border-border"
          }`}
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
            className="flex-1 rounded-lg border border-border bg-transparent px-3 py-2 text-sm text-foreground outline-none placeholder:text-muted-foreground"
          />
          <button
            type="button"
            onClick={() => void handleSubmit()}
            disabled={loading || !website.trim() || !command.trim()}
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground transition-opacity hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-35"
            aria-label="실행"
          >
            <Send className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>

      {error && (
        <p className="px-3 pb-3 text-xs text-muted-foreground" role="status">
          {error}
        </p>
      )}
    </div>
  )
}

export function CrawlerScraperBanner() {
  return (
    <div className="w-full min-w-0 rounded-3xl border border-border bg-card p-6 sm:p-8">
      <div className="flex items-center gap-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-muted">
          <Bot className="h-4.5 w-4.5 text-foreground" aria-hidden="true" />
        </span>
        <div>
          <p className="text-xs font-mono tracking-widest uppercase text-muted-foreground">
            Web Crawler · Scraper
          </p>
          <p className="text-sm text-muted-foreground">사이트 주소와 자연어 명령으로 수집을 실행해 보세요</p>
        </div>
      </div>

      <h2 className="mt-4 text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
        원하는 사이트에서 말하는 대로 데이터를 모아보세요.
      </h2>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        왼쪽은 링크를 찾는 크롤러, 오른쪽은 본문을 추출하는 스크래퍼입니다. 사이트 주소를 넣고
        "재즈 관련 내용 찾아줘"처럼 자연어로 말하면 알아서 이해해서 실행합니다. 주소창의 링크를
        URL 칸에 드래그해서 놓을 수도 있어요.
      </p>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <CrawlerScraperPanel
          mode="crawler"
          title="링크 크롤러"
          description="페이지에서 원하는 키워드가 포함된 링크를 찾습니다."
          onSubmit={async (website, command) => {
            const { count, results } = await commandCrawl(website, command)
            return { count, keyword: results[0]?.keyword }
          }}
        />
        <CrawlerScraperPanel
          mode="scraper"
          title="본문 스크래퍼"
          description="페이지 본문에서 원하는 키워드가 포함된 문단을 추출합니다."
          onSubmit={async (website, command) => {
            const { count, results } = await commandScrape(website, command)
            return { count, keyword: results[0]?.keyword }
          }}
        />
      </div>
    </div>
  )
}

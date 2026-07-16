import { UserFacingError, UI_ERRORS, apiErrorOrFallback } from "@/lib/user-facing-error"

export type CrawlResultItem = {
  website: string
  keyword: string
  found_url: string
  link_text: string
}

export type ScrapeResultItem = {
  website: string
  keyword: string
  snippet: string
}

export async function commandCrawl(
  website: string,
  command: string
): Promise<{ count: number; results: CrawlResultItem[] }> {
  const res = await fetch("/api/star-craft/crawler/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ website, command }),
    cache: "no-store",
  })
  const data = (await res.json()) as { count?: number; results?: CrawlResultItem[]; error?: string }
  if (!res.ok) {
    throw new UserFacingError(apiErrorOrFallback(data.error, UI_ERRORS.crawlerFailed))
  }
  return { count: data.count ?? 0, results: data.results ?? [] }
}

export async function commandScrape(
  website: string,
  command: string
): Promise<{ count: number; results: ScrapeResultItem[] }> {
  const res = await fetch("/api/star-craft/scraper/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ website, command }),
    cache: "no-store",
  })
  const data = (await res.json()) as { count?: number; results?: ScrapeResultItem[]; error?: string }
  if (!res.ok) {
    throw new UserFacingError(apiErrorOrFallback(data.error, UI_ERRORS.scraperFailed))
  }
  return { count: data.count ?? 0, results: data.results ?? [] }
}

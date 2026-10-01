import type { MetadataRoute } from "next"

const SITE = "https://woojeongalex.cloud"

/**
 * 사람이 직접 들어갈 수 있는 화면만 싣는다.
 *
 * 곡별 상세(`/music-challenge/[id]`)는 넣지 않았다. 목록에서 링크로 닿을 수 있고,
 * 곡이 지워지면 사이트맵이 없는 주소를 가리키게 된다 — 그게 다시 404 다.
 */
export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date()
  const paths = [
    { path: "/", priority: 1 },
    { path: "/music-challenge", priority: 0.9 },
    { path: "/rhythm", priority: 0.9 },
    { path: "/analyze", priority: 0.5 },
    { path: "/instrument", priority: 0.5 },
    { path: "/speech", priority: 0.5 },
    { path: "/auth", priority: 0.3 },
  ]

  return paths.map(({ path, priority }) => ({
    url: `${SITE}${path}`,
    lastModified: now,
    changeFrequency: "weekly" as const,
    priority,
  }))
}

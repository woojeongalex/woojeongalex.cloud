import type { MetadataRoute } from "next"

/**
 * 크롤러가 제일 먼저 찾는 파일. 없으면 404 가 나고, 사이트맵도 알려 줄 길이 없다.
 *
 * `/api/` 를 막는 이유: 이 경로들은 백엔드로 넘기는 통로일 뿐 읽을 문서가 아니다.
 * 검색 결과에 JSON 이 뜨면 사람에게도 쓸모없고 크롤링 예산만 쓴다.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api/"],
    },
    sitemap: "https://woojeongalex.cloud/sitemap.xml",
  }
}

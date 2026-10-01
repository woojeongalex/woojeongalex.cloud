import { ArrowUpRight, Boxes, ExternalLink } from "lucide-react"

/**
 * 홈에서 팀 프로젝트(Arda / Eval-ATS)로 보내는 배너.
 *
 * **주소는 이 세 줄에만 둔다.**
 *
 * 처음에는 팀이 띄워 둔 주소만 걸었다. 그런데 그 둘은 **내가 통제하지 못한다** —
 * 이탈한 전 팀장 명의 인프라라 언제 꺼질지 모른다고 인수인계 문서가 적어 두었다.
 * 지원 중에 꺼지면 배너가 죽은 링크가 된다.
 *
 * 그래서 첫 버튼은 **내 포크**로 돌렸다. 팀 저장소의 정식 포크라 출처가 드러나고,
 * 거기 README 에 내가 맡은 범위가 적혀 있다. 팀 쪽이 사라져도 이건 남는다.
 */
const REPO_URL = "https://github.com/woojeongalex/Arda"
const SERVICE_URL = "https://seuk.suvisdev.cloud"
const DOCS_URL = "https://ats.suvisdev.cloud"

/** 팀 문서 사이트와 인수인계 문서가 같은 값을 적고 있는 것만 싣는다. */
const FACTS = [
  { label: "API", value: "107" },
  { label: "테이블", value: "28" },
  { label: "백엔드 시험", value: "1,165" },
  { label: "ADR", value: "36" },
]

export function TeamProjectBanner() {
  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-6xl px-4 py-12 md:py-14">
        <article className="glow-card relative overflow-hidden rounded-3xl border border-neon-violet/30 bg-card/80 p-6 backdrop-blur sm:p-8">
          {/* 보라색 광원 하나 — 이 섹션만 다른 색을 쓴다 */}
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-neon-violet/20 blur-3xl"
          />

          <div className="relative flex flex-col gap-7 lg:flex-row lg:items-center lg:justify-between lg:gap-10">
            <div className="min-w-0 max-w-2xl">
              <span className="inline-flex items-center gap-2 rounded-full border border-neon-violet/50 bg-neon-violet/10 px-3.5 py-1 font-orbitron text-[11px] font-bold tracking-[0.2em] text-neon-violet">
                <Boxes className="h-3.5 w-3.5" aria-hidden="true" />
                TEAM PROJECT
              </span>

              <h2 className="mt-5 font-display text-3xl tracking-tight text-white sm:text-4xl">
                Arda — AI 채용 관리 플랫폼
              </h2>

              <p className="mt-4 text-sm leading-7 text-muted-foreground sm:text-base">
                공고 등록부터 지원서 접수, AI 서류 심사, AI 면접 실시간 분석, 합불 통보까지
                한 곳에서 돌리는 채용 시스템입니다. React 웹과 Flutter 앱이 같은 FastAPI 를
                씁니다. <span className="text-foreground">최종 합불은 사람이 확정합니다.</span>
              </p>

              <dl className="mt-6 flex flex-wrap gap-x-7 gap-y-3">
                {FACTS.map((fact) => (
                  <div key={fact.label}>
                    <dt className="text-[11px] tracking-wide text-muted-foreground">{fact.label}</dt>
                    <dd className="font-orbitron text-lg font-bold tabular-nums text-neon-cyan">
                      {fact.value}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>

            <div className="flex shrink-0 flex-col gap-3 lg:w-60">
              <a
                href={REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="glow-button inline-flex items-center justify-center gap-2 rounded-full bg-neon-violet px-6 py-3.5 text-sm font-bold text-night-950"
              >
                코드와 담당 범위
                <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
              </a>
              <a
                href={SERVICE_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 rounded-full border border-neon-cyan/70 bg-night-950/70 px-6 py-3.5 text-sm font-semibold text-neon-cyan transition-colors hover:bg-neon-cyan/10"
              >
                <ExternalLink className="h-4 w-4" aria-hidden="true" />
                돌아가는 서비스
              </a>
              <p className="text-center text-[11px] leading-5 text-muted-foreground">
                서비스와{" "}
                <a
                  href={DOCS_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline underline-offset-2 hover:text-foreground"
                >
                  소개 문서
                </a>
                는 팀 SEUK 가 운영합니다
              </p>
            </div>
          </div>
        </article>
      </div>
    </section>
  )
}

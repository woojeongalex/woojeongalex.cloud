import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { CHALLENGE_TYPE_LABEL, type Challenge } from "@/lib/music-challenge-api"
import { cn } from "@/lib/utils"

type ChallengeCardProps = {
  challenge: Challenge
  /** 이미 도전해 본 곡이면 배지를 달아 재도전임을 알린다. */
  attempted?: boolean
  className?: string
}

/** 챌린지 한 곡 카드 — 홈 미리보기와 챌린지 목록이 같은 모양을 쓴다. */
export function ChallengeCard({ challenge, attempted, className }: ChallengeCardProps) {
  return (
    <Link
      href={`/music-challenge/${challenge.id}`}
      className={cn(
        "glow-card group flex flex-col rounded-3xl border border-border bg-card p-6",
        className
      )}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full border border-neon-cyan/50 bg-neon-cyan/10 px-3 py-1 text-xs font-medium text-neon-cyan">
          {CHALLENGE_TYPE_LABEL[challenge.challenge_type] ?? challenge.challenge_type}
        </span>
        {attempted && (
          <span className="rounded-full border border-neon-green/50 bg-neon-green/10 px-3 py-1 text-xs font-medium text-neon-green">
            도전한 곡
          </span>
        )}
      </div>
      <h3 className="mt-4 font-display text-xl text-white">{challenge.title}</h3>
      <p className="mt-3 line-clamp-3 flex-1 text-sm leading-6 text-muted-foreground">
        {challenge.description}
      </p>
      <span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-neon-pink">
        {attempted ? "다시 도전하기" : "도전하기"}
        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
      </span>
    </Link>
  )
}

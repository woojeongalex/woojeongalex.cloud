"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Gamepad2 } from "lucide-react"
import { fetchRhythmChart, type RhythmChart } from "@/lib/rhythm-api"

type RhythmCtaProps = {
  challengeId: number
}

/** 채보가 있을 때만 보이는 리듬 게임 입구. 불러오지 못해도 챌린지 화면은 그대로 둔다. */
export function RhythmCta({ challengeId }: RhythmCtaProps) {
  const [chart, setChart] = useState<RhythmChart | null>(null)

  useEffect(() => {
    let alive = true
    fetchRhythmChart(challengeId)
      .then((c) => {
        if (alive) setChart(c)
      })
      .catch(() => undefined)
    return () => {
      alive = false
    }
  }, [challengeId])

  if (!chart || chart.sheets.length === 0) return null

  const levels = chart.sheets.map((s) => s.level)
  return (
    <section className="mt-6 overflow-hidden rounded-3xl bg-zinc-950 p-6 text-white">
      <p className="text-sm font-medium text-sky-400">리듬 게임</p>
      <h2 className="mt-1 text-2xl font-semibold">떨어지는 노트를 박자에 맞춰 치기</h2>
      <p className="mt-2 text-sm leading-6 text-white/60">
        4키·7키, 쉬움·보통·어려움 (Lv.{Math.min(...levels)}~{Math.max(...levels)}). 키보드나
        터치로 치고, 끝나면 채보별 랭킹에 올라갑니다.
      </p>
      <Link
        href={`/music-challenge/${challengeId}/rhythm`}
        className="mt-5 inline-flex items-center gap-2 rounded-full bg-sky-500 px-6 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90"
      >
        <Gamepad2 className="h-4 w-4" aria-hidden="true" />
        리듬 게임 하기
      </Link>
    </section>
  )
}

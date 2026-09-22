"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Gamepad2, Keyboard, Smartphone, Trophy } from "lucide-react"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import { SynthBackdrop } from "@/components/common/synth-backdrop"
import {
  RHYTHM_DIFFICULTIES,
  RHYTHM_DIFFICULTY_LABEL,
  RHYTHM_KEYS,
  fetchRhythmSongs,
  type RhythmDifficulty,
  type RhythmSong,
} from "@/lib/rhythm-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"

// 난이도별 네온 배지 색 — 쉬움 초록, 보통 노랑, 어려움 핑크
const DIFFICULTY_BADGE: Record<RhythmDifficulty, string> = {
  easy: "border-neon-green/50 bg-neon-green/10 text-neon-green",
  normal: "border-neon-yellow/50 bg-neon-yellow/10 text-neon-yellow",
  hard: "border-neon-pink/50 bg-neon-pink/10 text-neon-pink",
}

function formatDuration(sec: number | null): string {
  if (!sec) return ""
  const s = Math.round(sec)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`
}

export default function RhythmSongsPage() {
  const [songs, setSongs] = useState<RhythmSong[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    fetchRhythmSongs()
      .then((s) => {
        if (alive) setSongs(s)
      })
      .catch((e) => {
        if (alive) setError(toUserFacingMessage(e, UI_ERRORS.requestFailed))
      })
    return () => {
      alive = false
    }
  }, [])

  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      {/* HERO — 석양과 격자 바닥 위에 게임 소개 */}
      <section className="relative overflow-hidden border-b border-border">
        <SynthBackdrop sunSize={280} horizon={0.66} />
        <div className="relative mx-auto flex min-h-[380px] max-w-5xl flex-col items-center px-4 pb-10 pt-12 text-center md:pt-16">
          <p className="inline-flex items-center gap-2 font-orbitron text-xs font-bold tracking-[0.25em] text-neon-cyan animate-in fade-in slide-in-from-bottom-4 duration-700">
            <Gamepad2 className="h-4 w-4" aria-hidden="true" />
            리듬 게임
          </p>
          <h1
            className="neon-text mt-4 font-display text-4xl leading-[1.1] text-white animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both sm:text-5xl"
            style={{ animationDelay: "120ms" }}
          >
            떨어지는 노트를 박자에 맞춰 치세요
          </h1>
          <p
            className="mt-5 max-w-2xl text-sm leading-7 text-foreground/85 animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both sm:text-base"
            style={{ animationDelay: "240ms" }}
          >
            AI가 만든 곡마다 4키·7키, 쉬움·보통·어려움 채보가 있습니다. 판정선에 닿는 순간
            키를 누르면 COOL, 롱노트는 끝까지 누르고 있으세요. 기록은 채보별 랭킹에 오릅니다.
          </p>
          <ul
            className="mt-auto flex flex-wrap justify-center gap-x-6 gap-y-2 rounded-full border border-border bg-night-950/70 px-5 py-2.5 text-sm text-foreground/85 backdrop-blur animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both"
            style={{ animationDelay: "360ms" }}
          >
            <li className="inline-flex items-center gap-2">
              <Keyboard className="h-4 w-4 text-neon-cyan" aria-hidden="true" />
              기본 키 4키 ← ↓ ↑ → · 7키 A S D Space J K L (게임 설정에서 바꿀 수 있어요)
            </li>
            <li className="inline-flex items-center gap-2">
              <Smartphone className="h-4 w-4 text-neon-cyan" aria-hidden="true" />
              휴대폰은 레인 터치
            </li>
            <li className="inline-flex items-center gap-2">
              <Trophy className="h-4 w-4 text-neon-yellow" aria-hidden="true" />
              로그인하면 랭킹 등록
            </li>
          </ul>
        </div>
      </section>

      <div className="mx-auto max-w-5xl px-4 py-10 md:py-14">
        <p className="font-orbitron text-xs tracking-[0.25em] text-neon-cyan">SELECT SONG</p>
        <h2 className="mt-2 font-display text-2xl text-white">곡 고르기</h2>

        {!songs && !error && <LoadingBlock label="곡을 불러오는 중입니다." className="mt-4 h-40" />}
        {error && <StatusNote className="mt-4">{error}</StatusNote>}
        {songs && songs.length === 0 && (
          <StatusNote className="mt-4">아직 리듬 게임 채보가 있는 곡이 없습니다.</StatusNote>
        )}

        {songs && songs.length > 0 && (
          <ul className="mt-4 grid gap-4 sm:grid-cols-2">
            {songs.map((song) => (
              <li key={song.challenge_id}>
                <Link
                  href={`/rhythm/${song.challenge_id}`}
                  className="glow-card block h-full rounded-3xl border border-border bg-card p-5"
                >
                  <p className="text-lg font-semibold leading-snug text-white">{song.title}</p>
                  <p className="mt-1 font-orbitron text-xs text-neon-cyan">
                    {song.bpm ? `BPM ${Math.round(song.bpm)}` : ""}
                    {song.duration ? ` · ${formatDuration(song.duration)}` : ""}
                  </p>
                  <table className="mt-4 w-full text-sm">
                    <tbody className="font-orbitron">
                      {RHYTHM_KEYS.map((k) => (
                        <tr key={k}>
                          <td className="w-12 py-1 text-xs font-bold text-muted-foreground">{k}키</td>
                          {RHYTHM_DIFFICULTIES.map((d) => {
                            const s = song.sheets.find((x) => x.keys === k && x.difficulty === d)
                            return (
                              <td key={d} className="py-1">
                                <span
                                  className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs ${DIFFICULTY_BADGE[d]} ${s ? "" : "opacity-40"}`}
                                >
                                  <span className="font-sans">{RHYTHM_DIFFICULTY_LABEL[d]}</span>
                                  {s ? `Lv.${s.level}` : "—"}
                                </span>
                              </td>
                            )
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  )
}

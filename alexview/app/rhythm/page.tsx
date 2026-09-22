"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Gamepad2, Keyboard, Smartphone, Trophy } from "lucide-react"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import {
  RHYTHM_DIFFICULTIES,
  RHYTHM_DIFFICULTY_LABEL,
  RHYTHM_KEYS,
  fetchRhythmSongs,
  type RhythmSong,
} from "@/lib/rhythm-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"

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
      <div className="mx-auto max-w-5xl px-4 py-10 md:py-14">
        <section className="overflow-hidden rounded-3xl bg-zinc-950 p-6 text-white sm:p-10">
          <p className="inline-flex items-center gap-2 text-sm font-medium text-sky-400">
            <Gamepad2 className="h-4 w-4" aria-hidden="true" />
            리듬 게임
          </p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
            떨어지는 노트를 박자에 맞춰 치세요
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-white/60">
            AI가 만든 곡마다 4키·7키, 쉬움·보통·어려움 채보가 있습니다. 판정선에 닿는 순간
            키를 누르면 COOL, 롱노트는 끝까지 누르고 있으세요. 기록은 채보별 랭킹에 오릅니다.
          </p>
          <ul className="mt-5 flex flex-wrap gap-x-6 gap-y-2 text-sm text-white/70">
            <li className="inline-flex items-center gap-2">
              <Keyboard className="h-4 w-4" aria-hidden="true" />
              4키 D F J K · 7키 S D F Space J K L
            </li>
            <li className="inline-flex items-center gap-2">
              <Smartphone className="h-4 w-4" aria-hidden="true" />
              휴대폰은 레인 터치
            </li>
            <li className="inline-flex items-center gap-2">
              <Trophy className="h-4 w-4" aria-hidden="true" />
              로그인하면 랭킹 등록
            </li>
          </ul>
        </section>

        <h2 className="mt-10 text-xl font-semibold">곡 고르기</h2>

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
                  className="block h-full rounded-3xl border border-border bg-card p-5 transition-colors hover:border-sky-500/60 hover:bg-accent/40"
                >
                  <p className="text-lg font-semibold leading-snug">{song.title}</p>
                  <p className="mt-1 font-mono text-xs text-muted-foreground">
                    {song.bpm ? `BPM ${Math.round(song.bpm)}` : ""}
                    {song.duration ? ` · ${formatDuration(song.duration)}` : ""}
                  </p>
                  <table className="mt-4 w-full text-sm">
                    <tbody className="font-mono">
                      {RHYTHM_KEYS.map((k) => (
                        <tr key={k}>
                          <td className="w-12 py-0.5 text-muted-foreground">{k}키</td>
                          {RHYTHM_DIFFICULTIES.map((d) => {
                            const s = song.sheets.find((x) => x.keys === k && x.difficulty === d)
                            return (
                              <td key={d} className="py-0.5">
                                <span className="text-xs text-muted-foreground">
                                  {RHYTHM_DIFFICULTY_LABEL[d]}{" "}
                                </span>
                                {s ? `Lv.${s.level}` : "—"}
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

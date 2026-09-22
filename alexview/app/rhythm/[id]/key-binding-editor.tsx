"use client"

import { useEffect, useState } from "react"
import { Keyboard, RotateCcw } from "lucide-react"
import type { RhythmKeys } from "@/lib/rhythm-api"
import { DEFAULT_BINDINGS, assignKey, isBindable, keyDisplayName } from "@/lib/rhythm-keys"
import { cn } from "@/lib/utils"

type KeyBindingEditorProps = {
  keys: RhythmKeys
  bindings: string[]
  onChange: (next: string[]) => void
}

/**
 * 레인마다 칠 키를 고른다. 버튼을 누르고 원하는 키를 치면 바뀐다(Esc 는 취소).
 * 다른 레인이 쓰던 키를 고르면 두 레인이 키를 맞바꾼다 — 같은 키가 두 레인에 붙지 않게.
 */
export function KeyBindingEditor({ keys, bindings, onChange }: KeyBindingEditorProps) {
  const [listening, setListening] = useState<number | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  useEffect(() => {
    if (listening === null) return
    const onKey = (e: KeyboardEvent) => {
      e.preventDefault()
      e.stopPropagation()
      if (e.code === "Escape" || e.key === "Escape") {
        setListening(null)
        return
      }
      if (!isBindable(e.code)) {
        setNotice("이 키는 쓸 수 없습니다. 다른 키를 눌러 주세요.")
        return
      }
      const swappedFrom = bindings.indexOf(e.code)
      onChange(assignKey(bindings, listening, e.code))
      setNotice(
        swappedFrom >= 0 && swappedFrom !== listening
          ? `${swappedFrom + 1}번 레인이 쓰던 키라서 두 레인의 키를 맞바꿨습니다.`
          : null
      )
      setListening(null)
    }
    // 캡처 단계에서 먼저 받아, 버튼 포커스 상태의 Space·Enter 가 버튼을 다시 누르지 않게 한다.
    window.addEventListener("keydown", onKey, true)
    return () => window.removeEventListener("keydown", onKey, true)
  }, [listening, bindings, onChange])

  const isDefault = bindings.every((c, i) => c === DEFAULT_BINDINGS[keys][i])

  return (
    <div className="mt-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground">
          <Keyboard className="h-4 w-4" aria-hidden="true" />
          키 설정 ({keys}키)
        </h2>
        <button
          type="button"
          onClick={() => {
            onChange([...DEFAULT_BINDINGS[keys]])
            setListening(null)
            setNotice(null)
          }}
          disabled={isDefault}
          className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground disabled:opacity-40"
        >
          <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
          기본값으로
        </button>
      </div>
      <div
        className="mt-2 grid gap-2"
        style={{ gridTemplateColumns: `repeat(${keys}, minmax(0, 1fr))` }}
      >
        {bindings.map((code, lane) => {
          const active = listening === lane
          return (
            <button
              key={lane}
              type="button"
              onClick={() => {
                setNotice(null)
                setListening(active ? null : lane)
              }}
              aria-label={`${lane + 1}번 레인 키: ${keyDisplayName(code)}. 눌러서 바꾸기`}
              aria-pressed={active}
              className={cn(
                "flex min-h-14 flex-col items-center justify-center rounded-xl border px-1 py-2 transition-all",
                active
                  ? "animate-pulse border-neon-pink bg-neon-pink/15 text-white shadow-[0_0_16px_-4px_#ff2e97]"
                  : "border-border bg-night-900 text-neon-cyan hover:border-neon-cyan/60"
              )}
            >
              <span className="text-[10px] text-muted-foreground">{lane + 1}번</span>
              <span className="font-orbitron text-sm font-bold">
                {active ? "키 입력…" : keyDisplayName(code)}
              </span>
            </button>
          )
        })}
      </div>
      <p className="mt-2 min-h-5 text-xs text-muted-foreground" aria-live="polite">
        {listening !== null
          ? `${listening + 1}번 레인에 쓸 키를 누르세요. 취소는 Esc.`
          : (notice ?? "레인 버튼을 누르고 원하는 키를 치면 바뀝니다. 휴대폰은 레인을 직접 터치합니다.")}
      </p>
    </div>
  )
}

/**
 * 리듬 게임 키 설정 — 레인마다 어떤 키(KeyboardEvent.code)로 칠지.
 *
 * 사람마다 브라우저에 저장한다(서버는 레인 번호만 받으므로 알 필요가 없다).
 * code 는 자판 배열과 상관없는 "자리" 이름이라, 한글 입력 상태여도 같은 키로 잡힌다.
 */

import { RHYTHM_KEY_CODES, type RhythmKeys } from "@/lib/rhythm-api"

export type KeyBindings = Record<RhythmKeys, string[]>

export const DEFAULT_BINDINGS: KeyBindings = {
  4: [...RHYTHM_KEY_CODES[4]],
  7: [...RHYTHM_KEY_CODES[7]],
}

// 게임 종료(Esc)나 브라우저·운영체제가 먼저 가져가는 키는 레인에 쓸 수 없다.
const BLOCKED = new Set([
  "Escape",
  "Tab",
  "MetaLeft",
  "MetaRight",
  "OSLeft",
  "OSRight",
  "ContextMenu",
  "F5",
  "F11",
  "F12",
])

export function isBindable(code: string): boolean {
  return code !== "" && !BLOCKED.has(code)
}

const ARROWS: Record<string, string> = {
  ArrowLeft: "←",
  ArrowRight: "→",
  ArrowUp: "↑",
  ArrowDown: "↓",
}

const NAMED: Record<string, string> = {
  Space: "␣",
  Enter: "⏎",
  Backspace: "⌫",
  ShiftLeft: "LShift",
  ShiftRight: "RShift",
  ControlLeft: "LCtrl",
  ControlRight: "RCtrl",
  AltLeft: "LAlt",
  AltRight: "RAlt",
  Semicolon: ";",
  Quote: "'",
  Comma: ",",
  Period: ".",
  Slash: "/",
  Backslash: "\\",
  BracketLeft: "[",
  BracketRight: "]",
  Minus: "-",
  Equal: "=",
  Backquote: "`",
  CapsLock: "Caps",
}

/** 무대 키 자리·설정 버튼에 쓸 짧은 글자. */
export function keyLabel(code: string): string {
  if (ARROWS[code]) return ARROWS[code]
  if (NAMED[code]) return NAMED[code]
  if (/^Key[A-Z]$/.test(code)) return code.slice(3)
  if (/^Digit[0-9]$/.test(code)) return code.slice(5)
  if (/^Numpad[0-9]$/.test(code)) return `N${code.slice(6)}`
  return code.replace(/^Numpad/, "N")
}

/** 설정 화면 안내용 긴 이름(␣ → Space). */
export function keyDisplayName(code: string): string {
  return code === "Space" ? "Space" : keyLabel(code)
}

/**
 * code 가 비어 오는 입력기(일부 모바일 키보드, 자동화 도구)를 위한 대체 비교값 — KeyboardEvent.key 를
 * 소문자로 바꾼 것과 맞춘다. 알 수 없으면 빈 문자열(대체 비교 안 함).
 */
export function keyNameFor(code: string): string {
  if (code === "Space") return " "
  if (code.startsWith("Arrow")) return code.toLowerCase()
  if (/^Key[A-Z]$/.test(code)) return code.slice(3).toLowerCase()
  if (/^Digit[0-9]$/.test(code)) return code.slice(5)
  const symbol = NAMED[code]
  return symbol && symbol.length === 1 ? symbol : ""
}

/** 저장된 값이 깨졌거나 옛 형식이면 기본값으로 돌린다. 레인 수가 맞고 키가 겹치지 않아야 한다. */
export function normalizeBindings(raw: unknown): KeyBindings {
  const out: KeyBindings = { 4: [...DEFAULT_BINDINGS[4]], 7: [...DEFAULT_BINDINGS[7]] }
  if (!raw || typeof raw !== "object") return out
  for (const keys of [4, 7] as const) {
    const list = (raw as Record<string, unknown>)[String(keys)]
    if (
      Array.isArray(list) &&
      list.length === keys &&
      list.every((c) => typeof c === "string" && isBindable(c)) &&
      new Set(list).size === keys
    ) {
      out[keys] = [...(list as string[])]
    }
  }
  return out
}

/** lane 에 code 를 넣는다. 다른 레인이 이미 쓰던 키면 두 레인의 키를 맞바꾼다. */
export function assignKey(current: string[], lane: number, code: string): string[] {
  const next = [...current]
  const other = next.indexOf(code)
  if (other >= 0 && other !== lane) next[other] = next[lane]
  next[lane] = code
  return next
}

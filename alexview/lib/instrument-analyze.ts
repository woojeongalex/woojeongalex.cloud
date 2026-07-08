export type InstrumentTuningResult = {
  tuningAccuracy: number
  pitchDeviationCents: number
  summary: string
  stringReadings: { label: string; cents: number }[]
}

const GUITAR_STRINGS = ["E2", "A2", "D3", "G3", "B3", "E4"] as const
const PIANO_KEYS = ["A0", "C4", "E4", "A4"] as const

/** 마이크 녹음 길이 기반 데모 튜닝 점수 (서버 저장용). */
export function demoInstrumentTuning(
  instrumentId: "guitar" | "piano",
  durationSec: number
): InstrumentTuningResult {
  const labels = instrumentId === "guitar" ? GUITAR_STRINGS : PIANO_KEYS
  const base = instrumentId === "guitar" ? 70 : 74
  const tuningAccuracy = Math.min(
    100,
    Math.max(50, base + Math.min(25, Math.floor(durationSec / 2)))
  )
  const pitchDeviationCents = Math.max(
    0,
    Math.round((100 - tuningAccuracy) * 0.8)
  )
  const stringReadings = labels.map((label, i) => ({
    label,
    cents: Math.round(pitchDeviationCents * (0.6 + (i % 3) * 0.15)),
  }))
  const summary =
    instrumentId === "guitar"
      ? `기타 튜닝 정확도 ${tuningAccuracy}%입니다. 편차가 큰 현부터 조율해 보세요.`
      : `피아노 음정·튜닝 점수 ${tuningAccuracy}%입니다. 중역·고음역을 차례로 확인해 보세요.`

  return {
    tuningAccuracy,
    pitchDeviationCents,
    summary,
    stringReadings,
  }
}

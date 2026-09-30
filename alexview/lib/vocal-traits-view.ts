/**
 * 발성 진단을 화면에 쓸 줄로 바꾼다.
 *
 * 숫자를 그대로 늘어놓으면 "47센트"가 좋은 건지 나쁜 건지 알 수 없다. 각 줄에
 * 값과 함께 그 값이 무슨 뜻인지를 한 마디로 붙인다.
 *
 * 재지 못한 항목은 줄째로 뺀다. 빈 칸을 보여 주면 측정에 실패한 것인지 결과가
 * 0인 것인지 구별되지 않는다.
 */

import type { VocalTraits } from "@/lib/music-challenge-api"

export type TraitRow = {
  label: string
  value: string
  note: string
  /** 나쁠수록 true — 화면에서 눈에 띄게 표시한다 */
  warn: boolean
}

const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

export function midiName(midi: number): string {
  const n = Math.round(midi)
  return `${NOTE_NAMES[((n % 12) + 12) % 12]}${Math.floor(n / 12) - 1}`
}

export function traitRows(t: VocalTraits): TraitRow[] {
  const rows: TraitRow[] = []

  rows.push({
    label: "소리 낸 비율",
    value: `${t.voiced_ratio}%`,
    note:
      t.voiced_ratio >= 90
        ? "음표를 거의 빠뜨리지 않았습니다"
        : t.voiced_ratio >= 70
          ? "군데군데 소리가 비었습니다"
          : "부르지 못하고 넘어간 구간이 많습니다",
    warn: t.voiced_ratio < 70,
  })

  if (t.pitch_bias_cents !== null) {
    const size = Math.abs(t.pitch_bias_cents)
    const dir = t.pitch_bias_cents > 0 ? "높게" : "낮게"
    rows.push({
      label: "음정 쏠림",
      value: `${t.pitch_bias_cents > 0 ? "+" : ""}${t.pitch_bias_cents}센트`,
      note:
        size < 15
          ? "한쪽으로 치우치지 않았습니다"
          : `전반적으로 ${dir} 부릅니다 (반음의 ${Math.round((size / 100) * 100)}%)`,
      warn: size >= 30,
    })
  }

  if (t.flat_ratio !== null) {
    rows.push({
      label: "어긋난 방향",
      value: `아래 ${t.flat_ratio}% · 위 ${100 - t.flat_ratio}%`,
      note:
        t.flat_ratio >= 65
          ? "음이 아래로 쳐지는 버릇이 있습니다"
          : t.flat_ratio <= 35
            ? "음이 위로 뜨는 버릇이 있습니다"
            : "한쪽으로 치우치지 않았습니다",
      warn: t.flat_ratio >= 65 || t.flat_ratio <= 35,
    })
  }

  if (t.low_accuracy !== null && t.high_accuracy !== null) {
    const gap = t.low_accuracy - t.high_accuracy
    rows.push({
      label: "음역별 정확도",
      value: `낮은 음 ${t.low_accuracy}% · 높은 음 ${t.high_accuracy}%`,
      note:
        gap >= 15
          ? "높은 음에서 더 무너집니다"
          : gap <= -15
            ? "낮은 음에서 더 무너집니다"
            : "위아래가 고릅니다",
      warn: Math.abs(gap) >= 15,
    })
  }

  if (t.attack_delay_ms !== null) {
    rows.push({
      label: "음 잡는 시간",
      value: `${t.attack_delay_ms}ms`,
      note:
        t.attack_delay_ms < 120
          ? "첫 소리부터 음이 맞습니다"
          : "음을 더듬어 찾는 편입니다",
      warn: t.attack_delay_ms >= 120,
    })
  }

  if (t.vibrato_extent_cents !== null && t.vibrato_rate_hz !== null) {
    const steady =
      t.vibrato_rate_hz >= 4.5 &&
      t.vibrato_rate_hz <= 7.5 &&
      t.vibrato_extent_cents >= 20 &&
      t.vibrato_extent_cents <= 100
    rows.push({
      label: "긴 음의 흔들림",
      value: `${t.vibrato_extent_cents}센트 · ${t.vibrato_rate_hz}Hz`,
      note: steady ? "고른 비브라토입니다" : "비브라토라기보다 음정이 흔들립니다",
      warn: !steady,
    })
  }

  if (t.comfort_low_midi !== null && t.comfort_high_midi !== null) {
    rows.push({
      label: "편한 음역",
      value: `${midiName(t.comfort_low_midi)} ~ ${midiName(t.comfort_high_midi)}`,
      note: "이 구간에서 가장 정확했습니다. 다음 곡을 이 음역에 맞춰 골라 드립니다",
      warn: false,
    })
  }

  if (t.weak_note_count > 0) {
    rows.push({
      label: "놓친 음표",
      value: `${t.weak_note_count}개`,
      note: "절반도 맞히지 못한 음표입니다",
      warn: true,
    })
  }

  return rows
}

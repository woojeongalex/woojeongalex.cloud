export type SpeechFeedbackResult = {
  clarityScore: number
  paceScore: number
  toneScore: number
  summary: string
  feedbackPoints: string[]
}

/** 녹음 길이·주제 기반 데모 스피치 피드백 (서버 저장용). */
export function demoSpeechFeedback(
  topicId: string,
  durationSec: number
): SpeechFeedbackResult {
  const base = 62 + Math.min(28, Math.floor(durationSec / 2))
  const clarityScore = Math.min(100, base + 4)
  const paceScore = Math.min(100, base)
  const toneScore = Math.min(100, base + 2)
  const topicLabel =
    topicId === "presentation"
      ? "발표"
      : topicId === "interview"
        ? "면접"
        : topicId === "pronunciation"
          ? "발음"
          : "일상 대화"

  return {
    clarityScore,
    paceScore,
    toneScore,
    summary: `${topicLabel} 연습 기준으로 말하기 균형이 양호합니다. 다음에는 문장 끝 호흡을 의식해 보세요.`,
    feedbackPoints: [
      "문장 사이 0.5초 호흡을 두면 전달력이 좋아집니다.",
      "핵심 단어 앞에서 살짝 속도를 늦춰 보세요.",
      "마지막 음절을 또박또박 마무리해 주세요.",
    ],
  }
}

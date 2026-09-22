import { notFound } from "next/navigation"
import { RhythmGame } from "./rhythm-game"

type RhythmPlayPageProps = {
  params: Promise<{ id: string }>
}

export default async function RhythmPlayPage({ params }: RhythmPlayPageProps) {
  const { id } = await params
  const challengeId = Number(id)

  if (!Number.isInteger(challengeId) || challengeId <= 0) notFound()

  return <RhythmGame challengeId={challengeId} />
}

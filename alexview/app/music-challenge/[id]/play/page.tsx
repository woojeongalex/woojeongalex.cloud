import { notFound } from "next/navigation"
import { KaraokePlayer } from "./karaoke-player"

type KaraokePlayPageProps = {
  params: Promise<{ id: string }>
}

export default async function KaraokePlayPage({ params }: KaraokePlayPageProps) {
  const { id } = await params
  const challengeId = Number(id)

  if (!Number.isInteger(challengeId) || challengeId <= 0) notFound()

  return <KaraokePlayer challengeId={challengeId} />
}

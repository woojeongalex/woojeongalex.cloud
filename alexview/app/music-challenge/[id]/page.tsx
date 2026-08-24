import { notFound } from "next/navigation"
import { ChallengeDetail } from "./challenge-detail"

type PageProps = { params: Promise<{ id: string }> }

export default async function MusicChallengeDetailPage({ params }: PageProps) {
  const { id } = await params
  const challengeId = Number(id)

  if (!Number.isInteger(challengeId) || challengeId <= 0) notFound()

  return <ChallengeDetail challengeId={challengeId} />
}

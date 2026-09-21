import { notFound } from "next/navigation"
import { ChartStudio } from "./chart-studio"

type ChartStudioPageProps = {
  params: Promise<{ id: string }>
}

export default async function ChartStudioPage({ params }: ChartStudioPageProps) {
  const { id } = await params
  const challengeId = Number(id)

  if (!Number.isInteger(challengeId) || challengeId <= 0) notFound()

  return <ChartStudio challengeId={challengeId} />
}

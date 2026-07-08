"use client"

import Link from "next/link"
import { useEffect, useMemo, useState } from "react"

import {
  fetchWalterPassengers,
  getUploadedFileName,
  type WalterPassenger,
} from "@/lib/titanic-api"

const TABLE_COLUMNS: Array<{ key: keyof WalterPassenger; label: string }> = [
  { key: "passenger_id", label: "PassengerId" },
  { key: "survived", label: "Survived" },
  { key: "pclass", label: "Pclass" },
  { key: "name", label: "Name" },
  { key: "gender", label: "gender" },
  { key: "age", label: "Age" },
  { key: "sib_sp", label: "SibSp" },
  { key: "parch", label: "Parch" },
  { key: "ticket", label: "Ticket" },
  { key: "fare", label: "Fare" },
]

const ROWS_PER_PAGE = 30

export default function TitanicDetailPage() {
  const [fileName] = useState<string | null>(() => getUploadedFileName())
  const [rows, setRows] = useState<WalterPassenger[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)

  useEffect(() => {
    setCurrentPage(1)
  }, [fileName])

  useEffect(() => {
    if (!fileName) {
      setRows([])
      setTotal(0)
      setTotalPages(0)
      setError("업로드한 CSV 파일 정보가 없습니다. 먼저 업로드 페이지에서 CSV를 올려 주세요.")
      setLoading(false)
      return
    }

    let cancelled = false

    const run = async () => {
      setLoading(true)
      setError(null)
      try {
        const page = await fetchWalterPassengers({
          sourceFile: fileName,
          page: currentPage,
          size: ROWS_PER_PAGE,
        })
        if (cancelled) return
        setRows(page.rows)
        setTotal(page.total)
        setTotalPages(Math.max(1, page.total_pages))
      } catch (err) {
        if (cancelled) return
        const message = err instanceof Error ? err.message : "상세 데이터를 불러오지 못했습니다."
        setError(message)
        setRows([])
        setTotal(0)
        setTotalPages(0)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void run()

    return () => {
      cancelled = true
    }
  }, [currentPage, fileName])

  const pageNumbers = useMemo(() => {
    const visibleCount = 10
    const blockStart = Math.floor((currentPage - 1) / visibleCount) * visibleCount + 1
    const blockEnd = Math.min(totalPages, blockStart + visibleCount - 1)
    return Array.from({ length: blockEnd - blockStart + 1 }, (_, idx) => blockStart + idx)
  }, [currentPage, totalPages])

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-white px-4 py-10 text-zinc-900">
      <div className="mx-auto w-full max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold sm:text-4xl">타이타닉 CSV 상세</h1>
            <p className="mt-2 text-sm text-zinc-600">
              {fileName ? `파일: ${fileName}` : "업로드된 CSV 파일이 없습니다."}
            </p>
          </div>
          <Link
            href="/titanic"
            className="rounded-lg border border-zinc-300 bg-white px-4 py-2 text-sm font-medium text-zinc-900 transition-colors hover:bg-zinc-50"
          >
            업로드 페이지로 돌아가기
          </Link>
        </div>

        {error ? (
          <section className="rounded-2xl border border-zinc-200 bg-zinc-50 p-6 text-sm text-zinc-600">
            {error}
          </section>
        ) : (
          <section className="overflow-hidden rounded-2xl border border-zinc-200 shadow-sm">
            <div className="max-h-[70vh] overflow-auto">
              <table className="min-w-full border-collapse text-sm">
                <thead className="sticky top-0 z-10 bg-zinc-100">
                  <tr>
                    {TABLE_COLUMNS.map((column) => (
                      <th
                        key={column.key}
                        className="whitespace-nowrap border-b border-zinc-200 px-3 py-2 text-left font-semibold text-zinc-700"
                      >
                        {column.label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={`${row.id}-${row.passenger_id}`} className="odd:bg-white even:bg-zinc-50">
                      {TABLE_COLUMNS.map((column) => (
                        <td
                          key={`${row.id}-${column.key}`}
                          className="whitespace-nowrap border-b border-zinc-100 px-3 py-2 text-zinc-800"
                        >
                          {row[column.key] ?? ""}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="relative flex items-center justify-between border-t border-zinc-200 bg-zinc-50 px-4 py-3">
              <p className="text-sm text-zinc-600">
                {loading
                  ? "데이터 로딩 중..."
                  : `페이지 ${currentPage} / ${totalPages} (페이지당 ${ROWS_PER_PAGE}명, 총 ${total}명)`}
              </p>
              <div className="absolute left-1/2 flex -translate-x-1/2 items-center gap-1">
                <button
                  type="button"
                  onClick={() =>
                    setCurrentPage((prev) => Math.max(1, Math.floor((prev - 1) / 10) * 10))
                  }
                  disabled={pageNumbers[0] === 1}
                  className="rounded-md border border-zinc-300 bg-white px-2.5 py-1.5 text-sm font-medium text-zinc-800 transition-colors hover:bg-zinc-100 disabled:cursor-not-allowed disabled:border-zinc-200 disabled:bg-zinc-100 disabled:text-zinc-400"
                >
                  이전
                </button>
                {pageNumbers.map((page) => (
                  <button
                    key={page}
                    type="button"
                    onClick={() => setCurrentPage(page)}
                    className={`rounded-md border px-2.5 py-1.5 text-sm font-medium transition-colors ${
                      page === currentPage
                        ? "border-zinc-900 bg-zinc-900 text-white"
                        : "border-zinc-300 bg-white text-zinc-800 hover:bg-zinc-100"
                    }`}
                  >
                    {page}
                  </button>
                ))}
                <button
                  type="button"
                  onClick={() =>
                    setCurrentPage((prev) =>
                      Math.min(totalPages, Math.floor((prev - 1) / 10) * 10 + 11),
                    )
                  }
                  disabled={pageNumbers[pageNumbers.length - 1] === totalPages}
                  className="rounded-md border border-zinc-300 bg-white px-2.5 py-1.5 text-sm font-medium text-zinc-800 transition-colors hover:bg-zinc-100 disabled:cursor-not-allowed disabled:border-zinc-200 disabled:bg-zinc-100 disabled:text-zinc-400"
                >
                  다음
                </button>
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  )
}

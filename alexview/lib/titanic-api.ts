export type WalterPassenger = {
  id: number
  source_file: string | null
  passenger_id: string | null
  survived: string | null
  pclass: string | null
  name: string | null
  gender: string | null
  age: string | null
  sib_sp: string | null
  parch: string | null
  ticket: string | null
  fare: string | null
  created_at: string | null
}

export type WalterPassengerPage = {
  source_file: string | null
  page: number
  size: number
  total: number
  total_pages: number
  rows: WalterPassenger[]
}

const UPLOADED_FILE_KEY = "titanic_uploaded_file_name"

export function getUploadedFileName(): string | null {
  if (typeof window === "undefined") return null
  return sessionStorage.getItem(UPLOADED_FILE_KEY)
}

export function setUploadedFileName(fileName: string): void {
  sessionStorage.setItem(UPLOADED_FILE_KEY, fileName)
}

export async function uploadTitanicCsv(file: File): Promise<{ file_name: string; count: number }> {
  const formData = new FormData()
  formData.append("file", file)

  let response: Response
  try {
    response = await fetch("/api/titanic/james/upload", { method: "POST", body: formData })
  } catch {
    throw new Error("백엔드 서버에 연결하지 못했습니다. 백엔드(8000)가 실행 중인지 확인해 주세요.")
  }

  const raw = await response.text()
  let data: { file_name?: string; count?: number; detail?: string }
  try {
    data = raw ? (JSON.parse(raw) as typeof data) : {}
  } catch {
    throw new Error("업로드 응답 형식이 올바르지 않습니다.")
  }

  if (!response.ok) {
    const detail = data.detail
    if (typeof detail === "string") {
      throw new Error(detail)
    }
    if (Array.isArray(detail)) {
      const first = detail[0] as { msg?: string; loc?: unknown[] } | undefined
      throw new Error(first?.msg ?? "CSV 형식이 올바르지 않습니다.")
    }
    throw new Error("업로드에 실패했습니다.")
  }

  return {
    file_name: String(data.file_name ?? file.name),
    count: Number(data.count ?? 0),
  }
}

export async function fetchWalterPassengers(options: {
  sourceFile?: string | null
  page: number
  size: number
}): Promise<WalterPassengerPage> {
  const params = new URLSearchParams({
    page: String(options.page),
    size: String(options.size),
  })
  if (options.sourceFile) {
    params.set("source_file", options.sourceFile)
  }

  let response: Response
  try {
    response = await fetch(`/api/titanic/walter/passengers?${params.toString()}`)
  } catch {
    throw new Error("백엔드 서버에 연결하지 못했습니다. 백엔드(8000)가 실행 중인지 확인해 주세요.")
  }

  const raw = await response.text()
  let payload: Partial<WalterPassengerPage> & { detail?: string }
  try {
    payload = raw ? (JSON.parse(raw) as Partial<WalterPassengerPage> & { detail?: string }) : {}
  } catch {
    throw new Error("상세 데이터 응답 형식이 올바르지 않습니다.")
  }

  if (!response.ok) {
    throw new Error(
      typeof payload.detail === "string" ? payload.detail : "상세 데이터를 불러오지 못했습니다.",
    )
  }

  return {
    source_file: payload.source_file ?? null,
    page: Number(payload.page ?? options.page),
    size: Number(payload.size ?? options.size),
    total: Number(payload.total ?? 0),
    total_pages: Number(payload.total_pages ?? 0),
    rows: Array.isArray(payload.rows) ? (payload.rows as WalterPassenger[]) : [],
  }
}

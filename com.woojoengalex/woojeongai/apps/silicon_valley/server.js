const express = require('express')
const cors = require('cors')

const app = express()
const PORT = 4000
const FASTAPI_BASE = process.env.FASTAPI_BASE || 'http://localhost:8000'

app.use(cors({ origin: 'http://localhost:3000' }))
app.use(express.json())

async function proxy(fastApiPath, res, next) {
  try {
    const upstream = await fetch(`${FASTAPI_BASE}${fastApiPath}`)
    if (!upstream.ok) throw new Error(`upstream ${fastApiPath} → ${upstream.status}`)
    const data = await upstream.json()
    res.json(data)
  } catch (err) {
    next(err)
  }
}

app.get('/health', (_req, res) =>
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
)

app.get('/api/admin/stats',                (_req, res, next) => proxy('/silicon_valley/admin/stats',                res, next))
app.get('/api/admin/service-stats',        (_req, res, next) => proxy('/silicon_valley/admin/service-stats',        res, next))
app.get('/api/admin/intent-distribution',  (_req, res, next) => proxy('/silicon_valley/admin/intent-distribution',  res, next))
app.get('/api/admin/passengers',           (_req, res, next) => proxy('/silicon_valley/admin/passengers',           res, next))
app.get('/api/admin/intent-logs',          (_req, res, next) => proxy('/silicon_valley/admin/intent-logs',          res, next))

app.use((err, _req, res, _next) => {
  console.error('[Admin Proxy Error]', err.message)
  res.status(502).json({ error: '서버 연결 실패', detail: err.message })
})

app.listen(PORT, () => {
  console.log(`Admin proxy  → http://localhost:${PORT}`)
  console.log(`FastAPI base → ${FASTAPI_BASE}`)
})

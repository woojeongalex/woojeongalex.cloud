'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

// ── 응답 타입 ────────────────────────────────────────────────────────────────
interface StatsRes {
  totalEvals:     number
  avgScore:       number
  intentLogCount: number
  passengerCount: number
}

interface ServiceStatsRes {
  vocalEvalRate:     number
  aiAccuracyRate:    number
  passengerDataRate: number
  speechEvalRate:    number
}

interface IntentDistItem { label: string; value: number }
interface IntentDistRes  { distribution: IntentDistItem[] }

interface PassengerItem {
  id:          number
  passengerId: number
  survived:    number
  pclass:      number
  name:        string
  gender:      string
  age:         number | null
  fare:        number | null
  embarked:    string
}
interface PassengersRes { data: PassengerItem[]; total: number }

interface IntentLogItem {
  id:         number
  timestamp:  string
  message:    string
  intent:     string
  confidence: number
}
interface IntentLogsRes { data: IntentLogItem[]; total: number }

type NavItem = 'dashboard' | 'intent-logs' | 'passengers'

// ── 색상 토큰 ─────────────────────────────────────────────────────────────────
// Grayscale-only tokens. Roles that used to be conveyed by hue (success/danger/
// category) are now conveyed by lightness: darker = higher emphasis/positive,
// lighter = lower emphasis/negative. See ConfidenceBadge / survived badge for
// the clearest examples of this convention.
const C = {
  black:    '#000000',
  white:    '#FFFFFF',
  bg:       '#F8F8F8',
  border:   '#E4E4E4',
  muted:    '#737373',
  dark:     '#0F1117',
  green:    '#18181B',
  greenBg:  '#F4F4F5',
  red:      '#A1A1AA',
  redBg:    '#F4F4F5',
  blue:     '#27272A',
  blueBg:   '#F4F4F5',
  amber:    '#71717A',
  amberBg:  '#F4F4F5',
  purple:   '#52525B',
  purpleBg: '#F4F4F5',
} as const

const API = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:4000'

// ── 헬퍼 ─────────────────────────────────────────────────────────────────────
async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`, { cache: 'no-store' })
  if (!res.ok) throw new Error(`${path} → ${res.status}`)
  return res.json() as Promise<T>
}

function num(v: number | null | undefined): number {
  return v ?? 0
}

function useIsMobile(breakpoint = 768) {
  const [isMobile, setIsMobile] = useState(false)
  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < breakpoint)
    check()
    window.addEventListener('resize', check)
    return () => window.removeEventListener('resize', check)
  }, [breakpoint])
  return isMobile
}

// ── 서브 컴포넌트 ─────────────────────────────────────────────────────────────
function Sparkline({ color, up }: { color: string; up: boolean }) {
  const pts = up ? '0,24 13,22 26,18 39,20 52,12 65,9 78,6'
                 : '0,8  13,12 26,10 39,16 52,14 65,20 78,22'
  return (
    <svg width={80} height={32} viewBox="0 0 80 32" style={{ display: 'block' }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth={1.5} strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  )
}

function IntentBadge({ intent }: { intent: string }) {
  const map: Record<string, { bg: string; color: string }> = {
    count:      { bg: '#F4F4F5', color: '#27272A' },
    personal:   { bg: '#F4F4F5', color: '#52525B' },
    importance: { bg: '#F4F4F5', color: '#71717A' },
    death:      { bg: '#F4F4F5', color: '#A1A1AA' },
    general:    { bg: '#F8F8F8', color: '#737373' },
  }
  const s = map[intent] ?? { bg: '#F8F8F8', color: '#737373' }
  return (
    <span style={{
      display: 'inline-block', padding: '3px 10px', fontSize: 11,
      fontWeight: 700, borderRadius: 4, background: s.bg, color: s.color,
      letterSpacing: '0.06em', textTransform: 'uppercase',
    }}>
      {intent}
    </span>
  )
}

function ConfidenceBadge({ value }: { value: number }) {
  const pct   = Math.round(value * 100)
  const color = pct >= 90 ? C.green : pct >= 75 ? C.amber : C.red
  const bg    = pct >= 90 ? C.greenBg : pct >= 75 ? C.amberBg : C.redBg
  return (
    <span style={{ display: 'inline-block', padding: '3px 10px', fontSize: 12, fontWeight: 700, borderRadius: 4, background: bg, color }}>
      {pct}%
    </span>
  )
}

function TH({ children }: { children: React.ReactNode }) {
  return (
    <th style={{
      padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 700,
      color: C.muted, letterSpacing: '0.08em', textTransform: 'uppercase',
      borderBottom: `1px solid ${C.border}`, background: '#FAFAFA',
      whiteSpace: 'nowrap',
    }}>
      {children}
    </th>
  )
}

const navItems: { key: NavItem; label: string; icon: string }[] = [
  { key: 'dashboard',   label: '대시보드',    icon: '◈' },
  { key: 'intent-logs', label: '인텐트 로그', icon: '≡' },
  { key: 'passengers',  label: '탑승객',      icon: '⊞' },
]

// ── 메인 컴포넌트 ─────────────────────────────────────────────────────────────
export default function AdminPage() {
  const isMobile = useIsMobile()
  const px = isMobile ? 16 : 40

  const [active, setActive]               = useState<NavItem>('dashboard')
  const [stats, setStats]                 = useState<StatsRes | null>(null)
  const [serviceStats, setServiceStats]   = useState<ServiceStatsRes | null>(null)
  const [intentDist, setIntentDist]       = useState<IntentDistItem[]>([])
  const [passengers, setPassengers]       = useState<PassengerItem[]>([])
  const [passengerTotal, setPassengerTotal] = useState<number>(0)
  const [intentLogs, setIntentLogs]       = useState<IntentLogItem[]>([])
  const [hoveredRow, setHoveredRow]       = useState<number | null>(null)
  const [isLoading, setIsLoading]         = useState(true)
  const [error, setError]                 = useState<string | null>(null)
  const [lastUpdated, setLastUpdated]     = useState('')

  const fetchAll = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [s, ss, id, p, il] = await Promise.all([
        apiFetch<StatsRes>('/api/admin/stats'),
        apiFetch<ServiceStatsRes>('/api/admin/service-stats'),
        apiFetch<IntentDistRes>('/api/admin/intent-distribution'),
        apiFetch<PassengersRes>('/api/admin/passengers'),
        apiFetch<IntentLogsRes>('/api/admin/intent-logs'),
      ])
      setStats(s)
      setServiceStats(ss)
      setIntentDist(id.distribution)
      setPassengers(p.data)
      setPassengerTotal(p.total)
      setIntentLogs(il.data)
      const now = new Date()
      setLastUpdated(now.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }))
    } catch {
      setError('데이터를 불러올 수 없습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchAll()
    const timer = setInterval(fetchAll, 30_000)
    return () => clearInterval(timer)
  }, [])

  const kpiCards = [
    { label: '총 음악 평가',   value: num(stats?.totalEvals).toLocaleString(),     color: C.blue,   up: true  },
    { label: '평균 점수',      value: `${num(stats?.avgScore)}점`,                 color: C.green,  up: true  },
    { label: '인텐트 로그',    value: num(stats?.intentLogCount).toLocaleString(), color: C.purple, up: true  },
    { label: '탑승객 데이터',  value: num(stats?.passengerCount).toLocaleString(), color: C.amber,  up: false },
  ]

  const serviceBars = serviceStats
    ? [
        { label: '보컬 평가 처리율',      value: serviceStats.vocalEvalRate,     color: C.blue   },
        { label: 'AI 인텐트 분류 정확도', value: serviceStats.aiAccuracyRate,    color: C.green  },
        { label: '탑승객 데이터 적재율',  value: serviceStats.passengerDataRate, color: C.amber  },
        { label: '스피치 평가 완료율',    value: serviceStats.speechEvalRate,    color: C.purple },
      ]
    : []

  // ── 레이아웃 ─────────────────────────────────────────────────────────────────
  return (
    <div style={{
      display: 'flex',
      flexDirection: isMobile ? 'column' : 'row',
      minHeight: '100vh',
      background: C.bg,
      fontFamily: 'inherit',
      fontSize: 14,
    }}>

      {/* ── 사이드바 (데스크탑) / 상단 헤더 (모바일) ── */}
      {isMobile ? (
        <header style={{ background: C.dark, color: C.white, flexShrink: 0 }}>
          {/* 모바일 타이틀 바 */}
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.08)',
          }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase' }}>Woojeong</div>
              <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.35)', letterSpacing: '0.08em' }}>Admin Console</div>
            </div>
            <Link href="/" style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', textDecoration: 'none' }}>← 메인</Link>
          </div>
          {/* 모바일 탭 */}
          <nav style={{ display: 'flex' }}>
            {navItems.map(({ key, label, icon }) => (
              <button
                key={key}
                onClick={() => setActive(key)}
                style={{
                  flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center',
                  gap: 3, padding: '10px 4px', fontSize: 10, fontWeight: active === key ? 700 : 400,
                  background: active === key ? 'rgba(255,255,255,0.12)' : 'transparent',
                  color: active === key ? C.white : 'rgba(255,255,255,0.4)',
                  border: 'none', cursor: 'pointer',
                  borderTop: active === key ? `2px solid ${C.white}` : '2px solid transparent',
                }}
              >
                <span style={{ fontSize: 16 }}>{icon}</span>
                {label}
              </button>
            ))}
          </nav>
        </header>
      ) : (
        <aside style={{ width: 220, background: C.dark, color: C.white, display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
          <div style={{ padding: '28px 24px 22px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
            <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: '0.18em', textTransform: 'uppercase' }}>Woojeong</div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', marginTop: 3, letterSpacing: '0.1em' }}>Admin Console</div>
          </div>
          <nav style={{ padding: '20px 0', flex: 1 }}>
            <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.25)', padding: '0 24px 12px', letterSpacing: '0.14em', textTransform: 'uppercase', fontWeight: 700 }}>
              Menu
            </div>
            {navItems.map(({ key, label, icon }) => (
              <button
                key={key}
                onClick={() => setActive(key)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 10, width: '100%',
                  padding: '11px 24px', fontSize: 13,
                  fontWeight: active === key ? 600 : 400,
                  background: active === key ? 'rgba(255,255,255,0.1)' : 'transparent',
                  color: active === key ? C.white : 'rgba(255,255,255,0.45)',
                  border: 'none', cursor: 'pointer', textAlign: 'left',
                  borderLeft: active === key ? `2px solid ${C.white}` : '2px solid transparent',
                }}
              >
                <span style={{ fontSize: 14 }}>{icon}</span>
                {label}
              </button>
            ))}
          </nav>
          <div style={{ padding: '16px 24px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
            <Link href="/" style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)', textDecoration: 'none' }}>← 메인으로</Link>
          </div>
        </aside>
      )}

      {/* ── Main ── */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>

        {/* Top bar */}
        <div style={{
          background: C.white, borderBottom: `1px solid ${C.border}`,
          padding: `0 ${px}px`, height: 52,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0,
        }}>
          <div style={{ fontSize: 12, color: C.muted, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            Admin&nbsp;/&nbsp;<span style={{ color: C.black, fontWeight: 600 }}>{navItems.find(n => n.key === active)?.label}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0, marginLeft: 12 }}>
            {lastUpdated && !isMobile && (
              <span style={{ fontSize: 11, color: C.muted }}>{lastUpdated} 업데이트</span>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', background: error ? C.red : C.green, display: 'inline-block', flexShrink: 0 }} />
              <span style={{ fontSize: 12, color: C.muted }}>{error ? '오프라인' : '연결됨'}</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: `24px ${px}px`, flex: 1, overflow: 'auto' }}>
          <h1 style={{ fontSize: isMobile ? 17 : 20, fontWeight: 700, color: C.black, margin: '0 0 20px', letterSpacing: '-0.3px' }}>
            {navItems.find(n => n.key === active)?.label}
          </h1>

          {error && (
            <div style={{
              background: C.bg, border: `1px solid ${C.border}`, borderLeft: `3px solid ${C.black}`,
              padding: '12px 16px', color: C.black, fontSize: 13, marginBottom: 20, borderRadius: 4,
            }}>
              ⚠ {error}
            </div>
          )}

          {/* ── 대시보드 ── */}
          {active === 'dashboard' && (
            <>
              {/* KPI 카드: 데스크탑 4열 / 모바일 2열 */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: isMobile ? 'repeat(2, 1fr)' : 'repeat(4, 1fr)',
                gap: isMobile ? 10 : 14,
                marginBottom: isMobile ? 14 : 20,
              }}>
                {kpiCards.map((kpi) => (
                  <div key={kpi.label} style={{
                    background: C.white, border: `1px solid ${C.border}`,
                    borderTop: `3px solid ${kpi.color}`, padding: isMobile ? '14px 14px 10px' : '18px 18px 14px',
                  }}>
                    <div style={{ fontSize: 10, color: C.muted, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 700, lineHeight: 1.3 }}>
                      {kpi.label}
                    </div>
                    <div style={{ fontSize: isMobile ? 22 : 28, fontWeight: 800, color: isLoading ? C.muted : C.black, margin: '8px 0 6px', letterSpacing: '-1px', lineHeight: 1 }}>
                      {isLoading ? '—' : kpi.value}
                    </div>
                    {!isMobile && (
                      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                        <Sparkline color={kpi.color} up={kpi.up} />
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* 하단 섹션: 데스크탑 2열 / 모바일 1열 */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: isMobile ? '1fr' : '1fr 320px',
                gap: isMobile ? 14 : 14,
              }}>
                {/* 서비스 처리율 */}
                <div style={{ background: C.white, border: `1px solid ${C.border}`, padding: '22px 24px' }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: C.black, marginBottom: 20 }}>서비스 처리율</div>
                  {isLoading ? (
                    <div style={{ fontSize: 13, color: C.muted }}>불러오는 중...</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                      {serviceBars.map((bar) => (
                        <div key={bar.label}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                            <span style={{ fontSize: 12, color: C.muted, fontWeight: 500 }}>{bar.label}</span>
                            <span style={{ fontSize: 12, fontWeight: 700, color: C.black }}>{bar.value}%</span>
                          </div>
                          <div style={{ height: 5, background: C.border, borderRadius: 3 }}>
                            <div style={{ height: 5, width: `${bar.value}%`, background: bar.color, borderRadius: 3 }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* 실시간 인텐트 분포 */}
                <div style={{ background: C.dark, padding: '22px 24px', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 18 }}>
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: C.green, display: 'inline-block', flexShrink: 0 }} />
                    <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.35)', letterSpacing: '0.12em', textTransform: 'uppercase', fontWeight: 700 }}>
                      실시간 인텐트 분포
                    </span>
                  </div>
                  <div style={{ fontSize: isMobile ? 28 : 36, fontWeight: 800, color: C.white, letterSpacing: '-1.5px', lineHeight: 1 }}>
                    {isLoading ? '—' : num(stats?.intentLogCount).toLocaleString()}
                  </div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)', marginBottom: 22, marginTop: 4 }}>오늘 분석 건수</div>
                  {intentDist.length === 0 ? (
                    <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.25)', flex: 1, display: 'flex', alignItems: 'center' }}>
                      데이터 없음
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, flex: 1 }}>
                      {intentDist.map((row) => (
                        <div key={row.label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', width: 66 }}>{row.label}</span>
                          <div style={{ flex: 1, height: 3, background: 'rgba(255,255,255,0.08)', borderRadius: 2 }}>
                            <div style={{ height: 3, width: `${row.value}%`, background: 'rgba(255,255,255,0.65)', borderRadius: 2 }} />
                          </div>
                          <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', width: 30, textAlign: 'right' }}>{row.value}%</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {/* ── 인텐트 로그 ── */}
          {active === 'intent-logs' && (
            <div style={{ background: C.white, border: `1px solid ${C.border}` }}>
              <div style={{ padding: '14px 20px', borderBottom: `1px solid ${C.border}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: 13, fontWeight: 700, color: C.black }}>인텐트 분석 로그</span>
                <span style={{ fontSize: 11, color: C.muted, background: C.bg, padding: '3px 10px', border: `1px solid ${C.border}`, borderRadius: 4 }}>
                  {isLoading ? '—' : `${intentLogs.length}건`}
                </span>
              </div>
              {isLoading ? (
                <div style={{ padding: '24px', fontSize: 13, color: C.muted }}>불러오는 중...</div>
              ) : intentLogs.length === 0 ? (
                <div style={{ padding: '40px 24px', fontSize: 13, color: C.muted, textAlign: 'center' }}>
                  인텐트 로그 데이터가 없습니다.
                </div>
              ) : (
                <div style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, minWidth: 520 }}>
                    <thead><tr><TH>#</TH><TH>시각</TH><TH>메시지</TH><TH>인텐트</TH><TH>신뢰도</TH></tr></thead>
                    <tbody>
                      {intentLogs.map((log) => (
                        <tr
                          key={log.id}
                          onMouseEnter={() => setHoveredRow(log.id)}
                          onMouseLeave={() => setHoveredRow(null)}
                          style={{ background: hoveredRow === log.id ? C.bg : C.white, borderBottom: `1px solid ${C.border}` }}
                        >
                          <td style={{ padding: '12px 16px', color: C.muted, fontFamily: 'monospace', fontSize: 12 }}>{log.id}</td>
                          <td style={{ padding: '12px 16px', color: C.muted, whiteSpace: 'nowrap', fontFamily: 'monospace', fontSize: 12 }}>{log.timestamp}</td>
                          <td style={{ padding: '12px 16px', color: C.black }}>{log.message}</td>
                          <td style={{ padding: '12px 16px' }}><IntentBadge intent={log.intent} /></td>
                          <td style={{ padding: '12px 16px' }}><ConfidenceBadge value={log.confidence} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* ── 탑승객 ── */}
          {active === 'passengers' && (
            <div style={{ background: C.white, border: `1px solid ${C.border}` }}>
              <div style={{ padding: '14px 20px', borderBottom: `1px solid ${C.border}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
                <span style={{ fontSize: 13, fontWeight: 700, color: C.black }}>타이타닉 탑승객 데이터</span>
                <span style={{ fontSize: 11, color: C.muted, background: C.bg, padding: '3px 10px', border: `1px solid ${C.border}`, borderRadius: 4, whiteSpace: 'nowrap' }}>
                  {isLoading ? '—' : `전체 ${passengerTotal.toLocaleString()}명 중 ${passengers.length}건`}
                </span>
              </div>
              {isLoading ? (
                <div style={{ padding: '24px', fontSize: 13, color: C.muted }}>불러오는 중...</div>
              ) : passengers.length === 0 ? (
                <div style={{ padding: '40px 24px', fontSize: 13, color: C.muted, textAlign: 'center' }}>
                  탑승객 데이터가 없습니다.
                </div>
              ) : (
                <div style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, minWidth: 600 }}>
                    <thead><tr><TH>ID</TH><TH>생존</TH><TH>등급</TH><TH>이름</TH><TH>성별</TH><TH>나이</TH><TH>요금</TH><TH>탑승항</TH></tr></thead>
                    <tbody>
                      {passengers.map((p) => (
                        <tr
                          key={p.id}
                          onMouseEnter={() => setHoveredRow(p.id)}
                          onMouseLeave={() => setHoveredRow(null)}
                          style={{ background: hoveredRow === p.id ? C.bg : C.white, borderBottom: `1px solid ${C.border}` }}
                        >
                          <td style={{ padding: '12px 16px', color: C.muted, fontFamily: 'monospace', fontSize: 12 }}>{p.passengerId}</td>
                          <td style={{ padding: '12px 16px' }}>
                            <span style={{
                              display: 'inline-block', padding: '3px 10px', fontSize: 11, fontWeight: 700, borderRadius: 4,
                              background: p.survived === 1 ? C.greenBg : C.redBg,
                              color:      p.survived === 1 ? C.green   : C.red,
                            }}>
                              {p.survived === 1 ? '생존' : '사망'}
                            </span>
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            <span style={{ fontWeight: 700, fontSize: 12, color: p.pclass === 1 ? C.amber : p.pclass === 2 ? C.blue : C.muted }}>
                              {p.pclass}등석
                            </span>
                          </td>
                          <td style={{ padding: '12px 16px', color: C.black, fontWeight: 500 }}>{p.name}</td>
                          <td style={{ padding: '12px 16px', color: C.muted }}>{p.gender === 'male' ? '남' : '여'}</td>
                          <td style={{ padding: '12px 16px', color: C.black }}>{p.age ?? <span style={{ color: C.muted }}>—</span>}</td>
                          <td style={{ padding: '12px 16px', color: C.muted }}>{p.fare != null ? `£${p.fare.toFixed(2)}` : '—'}</td>
                          <td style={{ padding: '12px 16px', color: C.muted }}>{p.embarked || '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

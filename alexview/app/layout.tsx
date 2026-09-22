import type { Metadata, Viewport } from 'next'
import { Black_Han_Sans, IBM_Plex_Sans_KR, JetBrains_Mono, Orbitron } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { SiteHeader } from '@/components/site-header'
import { ThemeProvider } from '@/components/theme-provider'
import './globals.css'

// 한글 글꼴은 파일이 커서 미리 받지 않는다(preload: false). 글자가 나올 때 필요한 조각만 받는다.
const plexKr = IBM_Plex_Sans_KR({
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
  variable: '--font-plex-kr',
  display: 'swap',
  preload: false,
})
const blackHan = Black_Han_Sans({
  weight: '400',
  subsets: ['latin'],
  variable: '--font-black-han',
  display: 'swap',
  preload: false,
})
const orbitron = Orbitron({
  weight: ['500', '700', '800'],
  subsets: ['latin'],
  variable: '--font-orbitron-face',
  display: 'swap',
})
const jetbrains = JetBrains_Mono({
  weight: ['500', '700'],
  subsets: ['latin'],
  variable: '--font-jetbrains',
  display: 'swap',
})

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0d0619',
}

export const metadata: Metadata = {
  title: 'IUEM — AI 음악 챌린지 · 리듬 게임',
  description: 'AI가 만든 곡을 부르고, 치고, 랭킹에 오르는 곳',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="ko"
      suppressHydrationWarning
      className={`${plexKr.variable} ${blackHan.variable} ${orbitron.variable} ${jetbrains.variable}`}
    >
      <body className="min-h-screen overflow-x-hidden font-sans antialiased">
        {/* 신스웨이브 한 가지 테마만 쓴다. dark: 변형이 늘 켜지도록 다크로 고정한다. */}
        <ThemeProvider attribute="class" forcedTheme="dark" defaultTheme="dark" enableSystem={false}>
          <SiteHeader />
          {children}
          {process.env.NODE_ENV === 'production' && <Analytics />}
        </ThemeProvider>
      </body>
    </html>
  )
}

import { cn } from "@/lib/utils"

type SynthBackdropProps = {
  className?: string
  /** 석양 지름(px). 작은 히어로에서는 줄인다. */
  sunSize?: number
  /** 지평선 위치 — 위에서부터의 비율(0~1) */
  horizon?: number
}

/**
 * 신스웨이브 히어로 배경 — 줄무늬 석양, 지평선, 앞으로 흘러오는 격자 바닥.
 *
 * 장식이라 스크린리더에서 숨기고 클릭도 받지 않는다. 부모는 relative + overflow-hidden 이어야 한다.
 * 격자는 CSS 애니메이션으로만 움직여서 JS 비용이 없고, 움직임 줄이기 설정이면 멈춘다.
 */
export function SynthBackdrop({ className, sunSize = 420, horizon = 0.68 }: SynthBackdropProps) {
  const top = `${horizon * 100}%`
  return (
    <div aria-hidden="true" className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}>
      {/* 줄무늬(아래쪽 절반)가 지평선 위로 보이도록 해를 조금 더 올린다. 휴대폰에서는 화면 폭의 70%까지만 */}
      <div
        className="synth-sun animate-sun-pulse absolute left-1/2 -translate-x-1/2"
        style={{
          width: `min(${sunSize}px, 70vw)`,
          height: `min(${sunSize}px, 70vw)`,
          top: `calc(${top} - min(${sunSize}px, 70vw) * 0.82)`,
        }}
      />
      <div
        className="synth-grid animate-synth-grid absolute -left-1/4 -right-1/4 h-[70%]"
        style={{ top }}
      />
      <div
        className="absolute inset-x-0 h-[3px] bg-neon-pink shadow-[0_0_24px_#ff2e97]"
        style={{ top }}
      />
      {/* 지평선 아래를 바탕색으로 서서히 덮어 글자가 격자에 묻히지 않게 한다 */}
      <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-background to-transparent" />
    </div>
  )
}

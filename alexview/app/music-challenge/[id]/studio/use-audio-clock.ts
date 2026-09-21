import { useEffect, useRef, useState } from "react"

/**
 * <audio> 의 재생 위치를 화면 갱신 주기로 읽는다.
 *
 * timeupdate 이벤트는 초당 4번 남짓이라 피아노 롤 재생선이 뚝뚝 끊긴다.
 * 재생 중에만 requestAnimationFrame 으로 읽고, 멈추면 루프를 끈다.
 *
 * src 는 이 훅이 붙을 <audio> 의 주소. 바뀌면 리스너를 다시 붙인다.
 */
export function useAudioClock(src: string | null) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [time, setTime] = useState(0)
  const [playing, setPlaying] = useState(false)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return
    let frame = 0
    const tick = () => {
      setTime(audio.currentTime)
      frame = requestAnimationFrame(tick)
    }
    const onPlay = () => {
      setPlaying(true)
      frame = requestAnimationFrame(tick)
    }
    const onStop = () => {
      setPlaying(false)
      cancelAnimationFrame(frame)
      setTime(audio.currentTime)
    }
    const onSeek = () => setTime(audio.currentTime)
    audio.addEventListener("play", onPlay)
    audio.addEventListener("pause", onStop)
    audio.addEventListener("ended", onStop)
    audio.addEventListener("seeked", onSeek)
    return () => {
      cancelAnimationFrame(frame)
      audio.removeEventListener("play", onPlay)
      audio.removeEventListener("pause", onStop)
      audio.removeEventListener("ended", onStop)
      audio.removeEventListener("seeked", onSeek)
    }
    // <audio> 는 데이터를 불러온 뒤에야 그려지므로 src 가 생길 때 다시 붙인다.
  }, [src])

  return { audioRef, time, playing }
}

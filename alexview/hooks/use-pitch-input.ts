import { useCallback, useRef, useState } from "react"
import { detectPitch, type PitchReading } from "@/lib/pitch-detect"

export type PitchInputState = "idle" | "requesting" | "ready" | "denied"

// 이보다 주기성이 흐린 소리(숨, 자음, 잡음)는 음으로 치지 않는다.
const MIN_CLARITY = 0.8

/**
 * 노래방·연주 화면용 마이크 — 실시간 음높이 읽기 + 녹음을 한 스트림으로 한다.
 *
 * 녹음과 음높이 분석을 따로 마이크를 열면 두 번 권한을 묻거나 시작 시점이 어긋난다.
 * 같은 스트림에 AnalyserNode 와 MediaRecorder 를 함께 붙인다.
 *
 * 자동 음량 조절·잡음 제거는 끈다. 둘 다 목소리를 뭉개서 음정 판정을 흐린다.
 * 에코 제거는 켠다. 스피커로 틀었을 때 반주가 마이크로 되돌아오는 걸 조금이라도 줄인다.
 */
export function usePitchInput() {
  const [state, setState] = useState<PitchInputState>("idle")
  const ctxRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const bufferRef = useRef<Float32Array<ArrayBuffer> | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  // 기기가 알려 주는 입출력 지연(초). 판정 시점을 이만큼 늦춘다.
  const latencyRef = useRef(0)

  const open = useCallback(async (): Promise<boolean> => {
    if (streamRef.current) return true
    setState("requesting")
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: false, autoGainControl: false },
      })
      const ctx = new AudioContext()
      const source = ctx.createMediaStreamSource(stream)
      const analyser = ctx.createAnalyser()
      analyser.fftSize = 2048
      source.connect(analyser)

      // latency 는 Chrome 이 알려 주지만 아직 TS DOM 타입에는 없다. 모르면 10ms 로 둔다.
      const settings = stream.getAudioTracks()[0]?.getSettings() as
        | (MediaTrackSettings & { latency?: number })
        | undefined
      const inputLatency = settings?.latency ?? 0.01
      const outputLatency = ctx.outputLatency || ctx.baseLatency || 0
      latencyRef.current = inputLatency + outputLatency

      streamRef.current = stream
      ctxRef.current = ctx
      analyserRef.current = analyser
      bufferRef.current = new Float32Array(analyser.fftSize)
      setState("ready")
      return true
    } catch {
      setState("denied")
      return false
    }
  }, [])

  /** 녹음을 시작한다. 곡 재생과 같은 순간에 부른다 */
  const startRecording = useCallback(() => {
    const stream = streamRef.current
    if (!stream) return
    void ctxRef.current?.resume()
    chunksRef.current = []
    const recorder = new MediaRecorder(stream)
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data)
    }
    recorder.start()
    recorderRef.current = recorder
  }, [])

  /** 지금 이 순간의 음높이. 음이 아니면 null */
  const read = useCallback((): PitchReading | null => {
    const analyser = analyserRef.current
    const buf = bufferRef.current
    const ctx = ctxRef.current
    if (!analyser || !buf || !ctx) return null
    analyser.getFloatTimeDomainData(buf)
    const reading = detectPitch(buf, ctx.sampleRate)
    return reading && reading.clarity >= MIN_CLARITY ? reading : null
  }, [])

  /** 녹음을 끝내고 녹음본을 돌려준다. 마이크도 닫는다 */
  const stop = useCallback(async (): Promise<Blob | null> => {
    const recorder = recorderRef.current
    let blob: Blob | null = null
    if (recorder && recorder.state !== "inactive") {
      blob = await new Promise<Blob>((resolve) => {
        recorder.onstop = () =>
          resolve(new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" }))
        recorder.stop()
      })
    }
    recorderRef.current = null
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    await ctxRef.current?.close().catch(() => undefined)
    ctxRef.current = null
    analyserRef.current = null
    setState("idle")
    return blob
  }, [])

  return { state, open, startRecording, read, stop, latencyRef }
}

/**
 * 브라우저 녹음 결과를 백엔드가 읽을 수 있는 WAV 로 변환한다.
 *
 * MediaRecorder 는 브라우저마다 webm/opus 또는 mp4/aac 만 내놓는데(wav·ogg 는
 * 지원하지 않는다), 백엔드의 soundfile 은 둘 다 디코딩하지 못하고 컨테이너에
 * ffmpeg 도 없다. 그대로 올리면 librosa 분석이 통째로 실패해 음정·박자 지표가
 * 비어버린다. 그래서 업로드 전에 브라우저에서 PCM 으로 풀어 WAV 로 다시 싼다.
 *
 * 샘플레이트는 기본으로 원본을 유지한다(보통 48kHz). 긴 곡을 올릴 때는 sampleRate
 * 옵션으로 줄인다 — 48kHz 모노는 1분에 약 5.8MB 다.
 */

function encodeWav(samples: Float32Array, sampleRate: number): Blob {
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)
  const writeString = (offset: number, text: string) => {
    for (let i = 0; i < text.length; i++) view.setUint8(offset + i, text.charCodeAt(i))
  }

  writeString(0, "RIFF")
  view.setUint32(4, 36 + samples.length * 2, true)
  writeString(8, "WAVE")
  writeString(12, "fmt ")
  view.setUint32(16, 16, true) // fmt 청크 길이
  view.setUint16(20, 1, true) // PCM
  view.setUint16(22, 1, true) // 모노
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true) // byte rate
  view.setUint16(32, 2, true) // block align
  view.setUint16(34, 16, true) // bits per sample
  writeString(36, "data")
  view.setUint32(40, samples.length * 2, true)

  let offset = 44
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const clamped = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(offset, clamped < 0 ? clamped * 0x8000 : clamped * 0x7fff, true)
  }
  return new Blob([buffer], { type: "audio/wav" })
}

type BlobToWavOptions = {
  /**
   * 지정하면 이 샘플레이트로 줄인다. 노래방 제출은 서버가 어차피 16kHz 로 분석하고,
   * 48kHz 그대로면 4분 곡이 23MB 라 AI 코칭(인라인 20MB 한도)이 건너뛰어진다.
   */
  sampleRate?: number
}

/** 여러 채널을 평균 내어 모노로 */
function toMono(buffer: AudioBuffer): Float32Array {
  const mono = new Float32Array(buffer.length)
  for (let ch = 0; ch < buffer.numberOfChannels; ch++) {
    const data = buffer.getChannelData(ch)
    for (let i = 0; i < buffer.length; i++) mono[i] += data[i] / buffer.numberOfChannels
  }
  return mono
}

/** 녹음 Blob → 모노 16bit WAV. 디코딩에 실패하면 null. */
export async function blobToWav(
  blob: Blob,
  options: BlobToWavOptions = {}
): Promise<Blob | null> {
  const AudioCtx =
    window.AudioContext ??
    (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
  if (!AudioCtx) return null

  const ctx = new AudioCtx()
  try {
    const decoded = await ctx.decodeAudioData(await blob.arrayBuffer())
    const target = options.sampleRate
    if (!target || target === decoded.sampleRate) {
      return encodeWav(toMono(decoded), decoded.sampleRate)
    }
    // 브라우저 내장 리샘플러(OfflineAudioContext)로 줄인다. 앞단에 저역 통과가 들어가
    // 직접 솎아 내는 것과 달리 에일리어싱이 생기지 않는다.
    const offline = new OfflineAudioContext(1, Math.ceil(decoded.duration * target), target)
    const source = offline.createBufferSource()
    source.buffer = decoded
    source.connect(offline.destination)
    source.start()
    const rendered = await offline.startRendering()
    return encodeWav(rendered.getChannelData(0), target)
  } catch {
    return null
  } finally {
    void ctx.close()
  }
}

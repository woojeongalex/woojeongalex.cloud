/**
 * 브라우저 녹음 결과를 백엔드가 읽을 수 있는 WAV 로 변환한다.
 *
 * MediaRecorder 는 브라우저마다 webm/opus 또는 mp4/aac 만 내놓는데(wav·ogg 는
 * 지원하지 않는다), 백엔드의 soundfile 은 둘 다 디코딩하지 못하고 컨테이너에
 * ffmpeg 도 없다. 그대로 올리면 librosa 분석이 통째로 실패해 음정·박자 지표가
 * 비어버린다. 그래서 업로드 전에 브라우저에서 PCM 으로 풀어 WAV 로 다시 싼다.
 *
 * 샘플레이트는 원본을 유지한다(보통 48kHz). 리샘플링은 아티팩트를 만들 수 있고,
 * 20MB 업로드 한도 안에서 수 분 길이까지 충분히 들어간다.
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

/** 녹음 Blob → 모노 16bit WAV. 디코딩에 실패하면 null. */
export async function blobToWav(blob: Blob): Promise<Blob | null> {
  const AudioCtx =
    window.AudioContext ??
    (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
  if (!AudioCtx) return null

  const ctx = new AudioCtx()
  try {
    const decoded = await ctx.decodeAudioData(await blob.arrayBuffer())
    const length = decoded.length
    const channels = decoded.numberOfChannels
    const mono = new Float32Array(length)

    for (let ch = 0; ch < channels; ch++) {
      const data = decoded.getChannelData(ch)
      for (let i = 0; i < length; i++) mono[i] += data[i] / channels
    }
    return encodeWav(mono, decoded.sampleRate)
  } catch {
    return null
  } finally {
    void ctx.close()
  }
}

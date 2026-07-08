"use client"

import type { VocalAnalysisResult } from "@/lib/analyze-media"
import {
  MediaAnalysisDropzone,
  type MediaDropzoneCopy,
  VOCAL_DROPZONE_COPY,
} from "@/components/media-analysis-dropzone"

type VocalVideoDropzoneProps = {
  copy?: MediaDropzoneCopy
  disabled?: boolean
  onStatusMessage: (message: string) => void
  onAnalysisComplete: (result: VocalAnalysisResult) => void
  onClear?: () => void
}

export function VocalVideoDropzone({
  copy = VOCAL_DROPZONE_COPY,
  ...rest
}: VocalVideoDropzoneProps) {
  return <MediaAnalysisDropzone copy={copy} {...rest} />
}

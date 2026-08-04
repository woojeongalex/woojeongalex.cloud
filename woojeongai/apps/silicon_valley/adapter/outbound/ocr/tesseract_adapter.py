"""Tesseract 기반 OCR 어댑터.

AWS Textract는 계정 단위 서비스 구독이 필요해 사용할 수 없다.
Tesseract는 컨테이너 안에서 직접 돌기 때문에 외부 의존성이 없다.
이미지는 여전히 S3에 적재되고, 여기서는 그 객체를 읽어 텍스트만 뽑는다.
"""

from __future__ import annotations

import asyncio
import io

import pytesseract
from PIL import Image

from core.matrix.aws_s3_manager import S3Manager
from silicon_valley.app.ports.output.ocr_port import OcrPort


class TesseractOcrAdapter(OcrPort):
    def __init__(self, s3_manager: S3Manager, lang: str = "kor+eng") -> None:
        self._s3 = s3_manager
        self._lang = lang

    def _detect_text(self, bucket: str, key: str) -> str:
        data = self._s3.get_bytes(key, bucket=bucket)
        with Image.open(io.BytesIO(data)) as image:
            text = pytesseract.image_to_string(image, lang=self._lang)
        return text.strip()

    async def extract(self, bucket: str, key: str) -> str:
        # Tesseract는 CPU-bound라 이벤트 루프를 막지 않도록 스레드풀로 넘긴다.
        return await asyncio.to_thread(self._detect_text, bucket, key)

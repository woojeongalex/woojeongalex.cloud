"""Tesseract 기반 OCR 어댑터.

AWS Textract는 계정 단위 서비스 구독이 필요해 사용할 수 없다.
Tesseract는 컨테이너 안에서 직접 돌기 때문에 외부 의존성이 없다.
"""

from __future__ import annotations

import asyncio
import io

import pytesseract
from PIL import Image, ImageOps

from silicon_valley.app.ports.output.ocr_port import OcrPort

# 폰 사진은 4000px가 넘는데 Tesseract는 그만한 해상도가 필요 없다.
# 긴 변을 이 값으로 줄이면 인식률은 유지하면서 처리 시간이 크게 줄어든다.
_MAX_EDGE = 1600


class TesseractOcrAdapter(OcrPort):
    def __init__(self, lang: str = "kor+eng") -> None:
        self._lang = lang

    def _prepare(self, image: Image.Image) -> Image.Image:
        # 폰 사진은 EXIF로만 회전 정보를 갖고 있어 그대로 넣으면 눕힌 채로 인식된다.
        image = ImageOps.exif_transpose(image)
        if max(image.size) > _MAX_EDGE:
            image.thumbnail((_MAX_EDGE, _MAX_EDGE), Image.LANCZOS)
        return image.convert("L")

    def _detect_text(self, data: bytes) -> str:
        with Image.open(io.BytesIO(data)) as image:
            text = pytesseract.image_to_string(self._prepare(image), lang=self._lang)
        return text.strip()

    async def extract(self, data: bytes) -> str:
        # Tesseract는 CPU-bound라 이벤트 루프를 막지 않도록 스레드풀로 넘긴다.
        return await asyncio.to_thread(self._detect_text, data)

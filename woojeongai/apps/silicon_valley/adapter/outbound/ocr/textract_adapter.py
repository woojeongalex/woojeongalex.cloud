from __future__ import annotations

import asyncio

import boto3

from silicon_valley.app.ports.output.ocr_port import OcrPort


class TextractOcrAdapter(OcrPort):
    def __init__(self, region: str = "ap-northeast-2") -> None:
        self._region = region
        self._client: boto3.client | None = None

    def _get_client(self) -> boto3.client:
        if self._client is None:
            self._client = boto3.client("textract", region_name=self._region)
        return self._client

    def _detect_text(self, bucket: str, key: str) -> str:
        response = self._get_client().detect_document_text(
            Document={"S3Object": {"Bucket": bucket, "Name": key}}
        )
        lines = [
            block["Text"]
            for block in response.get("Blocks", [])
            if block["BlockType"] == "LINE"
        ]
        return "\n".join(lines)

    async def extract(self, bucket: str, key: str) -> str:
        return await asyncio.to_thread(self._detect_text, bucket, key)

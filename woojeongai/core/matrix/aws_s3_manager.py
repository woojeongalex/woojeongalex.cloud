"""AWS S3 접근을 관리하는 공용 클라이언트.

core/matrix/redis_client.py와 동일한 프로세스 싱글턴 패턴을 따른다.
자격 증명은 코드에 하드코딩하지 않고 core/matrix/secret_manager.py의
Keymaker를 통해 backend/.env(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)에서만 읽는다.
"""

from __future__ import annotations

import boto3

from core.matrix.secret_manager import get_keymaker


class S3Manager:
    _instance: S3Manager | None = None

    def __init__(
        self,
        region_name: str | None = None,
        bucket: str | None = None,
    ) -> None:
        keymaker = get_keymaker()
        self._access_key = keymaker.get_secret("AWS_ACCESS_KEY_ID") or None
        self._secret_key = keymaker.get_secret("AWS_SECRET_ACCESS_KEY") or None
        self._region = (
            region_name or keymaker.get_secret("AWS_REGION") or "ap-northeast-2"
        )
        self._bucket = bucket or keymaker.get_secret("AWS_S3_BUCKET") or None
        self._client: boto3.client | None = None

    @classmethod
    def instance(cls) -> S3Manager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def _get_client(self) -> boto3.client:
        if self._client is None:
            self._client = boto3.client(
                "s3",
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
                region_name=self._region,
            )
        return self._client

    def _resolve_bucket(self, bucket: str | None) -> str:
        resolved = bucket or self._bucket
        if not resolved:
            raise ValueError("S3 버킷 이름이 필요합니다 (AWS_S3_BUCKET 미설정).")
        return resolved

    def list_buckets(self) -> list[str]:
        response = self._get_client().list_buckets()
        return [b["Name"] for b in response["Buckets"]]

    def list_objects(self, prefix: str = "", bucket: str | None = None) -> list[str]:
        response = self._get_client().list_objects_v2(
            Bucket=self._resolve_bucket(bucket), Prefix=prefix
        )
        return [obj["Key"] for obj in response.get("Contents", [])]

    def upload_file(self, local_path: str, key: str, bucket: str | None = None) -> None:
        self._get_client().upload_file(local_path, self._resolve_bucket(bucket), key)

    def download_file(
        self, key: str, local_path: str, bucket: str | None = None
    ) -> None:
        self._get_client().download_file(self._resolve_bucket(bucket), key, local_path)

    def delete_object(self, key: str, bucket: str | None = None) -> None:
        self._get_client().delete_object(Bucket=self._resolve_bucket(bucket), Key=key)


def get_s3_manager() -> S3Manager:
    return S3Manager.instance()

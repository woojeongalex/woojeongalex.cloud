from fastapi import Depends

from core.matrix.aws_s3_manager import get_s3_manager
from silicon_valley.adapter.outbound.s3.s3_image_storage_adapter import (
    S3ImageStorageAdapter,
)
from silicon_valley.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
from silicon_valley.app.ports.output.s3_image_storage_port import S3ImageStoragePort
from silicon_valley.app.use_cases.s3_image_upload_interactor import (
    S3ImageUploadInteractor,
)


def get_s3_image_storage_port() -> S3ImageStoragePort:
    return S3ImageStorageAdapter(s3_manager=get_s3_manager())


def get_s3_image_upload_use_case(
    storage: S3ImageStoragePort = Depends(get_s3_image_storage_port),
) -> S3ImageUploadUseCase:
    return S3ImageUploadInteractor(storage=storage)

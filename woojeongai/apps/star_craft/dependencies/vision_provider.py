import os

from star_craft.app.ports.input.vision_use_case import VisionUseCase
from star_craft.app.use_cases.vision_interactor import VisionInteractor
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db
from star_craft.adapter.outbound.repositories.vision_repository import VisionRepository
from star_craft.adapter.outbound.s3.s3_image_storage_gateway import S3ImageStorageGateway
from star_craft.app.ports.output.image_storage_gateway import ImageStorageGateway
from star_craft.app.ports.output.vision_port import VisionPort

_S3_BUCKET = os.getenv("VISION_S3_BUCKET", "")
_AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")


"""
Vision 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(VisionRepository, S3ImageStorageGateway)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(VisionUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""

def get_vision_repository(
    db: AsyncSession = Depends(get_db)
) -> VisionPort:
    return VisionRepository(session=db)


def get_vision_storage_gateway() -> ImageStorageGateway:
    return S3ImageStorageGateway(bucket=_S3_BUCKET, region=_AWS_REGION)


def get_vision_use_case(
    repository: VisionPort = Depends(get_vision_repository),
    storage: ImageStorageGateway = Depends(get_vision_storage_gateway),
) -> VisionUseCase:
    return VisionInteractor(repository=repository, storage=storage)

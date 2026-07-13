from fastapi import APIRouter

from star_craft.adapter.inbound.api.v1.vision_router import vision_router

star_craft_router = APIRouter(prefix="/star-craft", tags=["star-craft"])
star_craft_router.include_router(vision_router)

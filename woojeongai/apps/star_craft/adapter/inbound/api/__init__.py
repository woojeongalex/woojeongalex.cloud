from fastapi import APIRouter

from star_craft.adapter.inbound.api.v1.convnext_router import convnext_router
from star_craft.adapter.inbound.api.v1.crawler_router import crawler_router
from star_craft.adapter.inbound.api.v1.scraper_router import scraper_router
from star_craft.adapter.inbound.api.v1.vision_router import vision_router

star_craft_router = APIRouter(prefix="/star-craft", tags=["star-craft"])
star_craft_router.include_router(vision_router)
star_craft_router.include_router(crawler_router)
star_craft_router.include_router(scraper_router)
star_craft_router.include_router(convnext_router)

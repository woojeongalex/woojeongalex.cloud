from fastapi import APIRouter

from silicon_valley.adapter.inbound.api.v1.admin_stats_router import admin_stats_router
from silicon_valley.adapter.inbound.api.v1.piper_bighetti_hr_router import (
    bighetti_hr_router,
)
from silicon_valley.adapter.inbound.api.v1.piper_dinesh_dash_router import (
    dinesh_dash_router,
)
from silicon_valley.adapter.inbound.api.v1.piper_dunn_coo_router import dunn_coo_router
from silicon_valley.adapter.inbound.api.v1.piper_gilfoyle_system_router import (
    gilfoyle_system_router,
)
from silicon_valley.adapter.inbound.api.v1.piper_hendricks__ceo_router import (
    hendricks_ceo_router,
)
from silicon_valley.adapter.inbound.api.v1.semantic_router import semantic_chat_router

silicon_valley_router = APIRouter(prefix="/silicon_valley", tags=["silicon_valley"])

silicon_valley_router.include_router(admin_stats_router)
silicon_valley_router.include_router(bighetti_hr_router)
silicon_valley_router.include_router(dinesh_dash_router)
silicon_valley_router.include_router(dunn_coo_router)
silicon_valley_router.include_router(gilfoyle_system_router)
silicon_valley_router.include_router(hendricks_ceo_router)
silicon_valley_router.include_router(semantic_chat_router)

__all__ = ["silicon_valley_router"]

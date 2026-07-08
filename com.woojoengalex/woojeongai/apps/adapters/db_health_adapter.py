from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DbHealthAdapter:
    @staticmethod
    async def neon_time_check(db: AsyncSession) -> dict:
        try:
            result = await db.execute(text("SELECT NOW();"))
            now = result.scalar()
            return {"status": "success", "neon_time": now}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

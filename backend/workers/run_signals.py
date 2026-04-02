import asyncio

from workers.celery_app import celery_app
from database import async_session


@celery_app.task(name="run_signal_engine")
def run_signal_engine_task(tenant_id: str):
    """Celery task: run signal engine for a tenant."""
    asyncio.run(_run(tenant_id))


async def _run(tenant_id: str):
    import uuid
    from services.signal_engine import run_signal_engine

    async with async_session() as db:
        result = await run_signal_engine(db, uuid.UUID(tenant_id))
        return result


@celery_app.task(name="run_all_tenants")
def run_all_tenants_task():
    """Celery task: run signal engine for all active tenants."""
    asyncio.run(_run_all())


async def _run_all():
    from sqlalchemy import select
    from models.tenant import WwTenant
    from services.signal_engine import run_signal_engine

    async with async_session() as db:
        result = await db.execute(
            select(WwTenant).where(WwTenant.is_active == True)
        )
        tenants = result.scalars().all()

        for tenant in tenants:
            try:
                await run_signal_engine(db, tenant.id)
            except Exception:
                continue

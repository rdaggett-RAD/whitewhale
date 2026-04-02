import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.tenant import WwTenant, WwUser
from models.signal import WwSignal
from models.action import WwActionQueue
from models.delivery import WwSentLog
from routers.auth import get_current_user
from services.integrations import check_all_integrations

router = APIRouter(prefix="/api/admin", tags=["admin"])


# --- Auth guard ---


async def require_admin(user: WwUser = Depends(get_current_user)) -> WwUser:
    if user.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# --- Schemas ---


class TenantCreate(BaseModel):
    name: str
    slug: str
    plan: str = "starter"


class TenantUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    plan: str | None = None
    is_active: bool | None = None


class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    plan: str
    is_active: bool

    model_config = {"from_attributes": True}


# --- Endpoints ---


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    req: TenantCreate,
    db: AsyncSession = Depends(get_db),
    user: WwUser = Depends(require_admin),
):
    existing = await db.execute(select(WwTenant).where(WwTenant.slug == req.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Slug already exists")

    tenant = WwTenant(name=req.name, slug=req.slug, plan=req.plan)
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.get("/tenants", response_model=list[TenantResponse])
async def list_tenants(
    db: AsyncSession = Depends(get_db),
    user: WwUser = Depends(require_admin),
):
    result = await db.execute(select(WwTenant).order_by(WwTenant.created_at.desc()))
    return result.scalars().all()


@router.patch("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: uuid.UUID,
    req: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    user: WwUser = Depends(require_admin),
):
    result = await db.execute(select(WwTenant).where(WwTenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    update_data = req.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(update(WwTenant).where(WwTenant.id == tenant_id).values(**update_data))
        await db.commit()
        await db.refresh(tenant)
    return tenant


@router.get("/tenants/{tenant_id}/usage")
async def tenant_usage(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: WwUser = Depends(require_admin),
):
    signal_count = await db.execute(
        select(func.count()).select_from(WwSignal).where(WwSignal.tenant_id == tenant_id)
    )
    action_count = await db.execute(
        select(func.count()).select_from(WwActionQueue).where(WwActionQueue.tenant_id == tenant_id)
    )
    sent_count = await db.execute(
        select(func.count()).select_from(WwSentLog).where(WwSentLog.tenant_id == tenant_id)
    )
    return {
        "tenant_id": str(tenant_id),
        "signals": signal_count.scalar() or 0,
        "actions": action_count.scalar() or 0,
        "sent": sent_count.scalar() or 0,
    }


@router.post("/tenants/{tenant_id}/seed")
async def seed_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: WwUser = Depends(require_admin),
):
    from services.seed import seed_f3_growth

    result = await db.execute(select(WwTenant).where(WwTenant.id == tenant_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Tenant not found")

    await seed_f3_growth(db, tenant_id)
    return {"status": "seeded", "tenant_id": str(tenant_id)}


@router.get("/integrations")
async def integrations_status(user: WwUser = Depends(require_admin)):
    results = await check_all_integrations()
    return {"integrations": results}

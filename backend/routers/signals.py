import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.signal import WwSignal
from backend.models.tenant import WwUser
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/api/signals", tags=["signals"])


# --- Schemas ---


class SignalResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    company_id: uuid.UUID | None
    white_whale_id: uuid.UUID | None
    signal_type: str
    signal_source: str | None
    signal_summary: str
    signal_url: str | None
    signal_date: datetime | None
    service_category_id: uuid.UUID | None
    classification_confidence: int | None
    classification_rationale: str | None
    urgency_score: int | None
    has_connection: bool
    connection_count: int
    opportunity_type: str | None
    status: str
    detected_at: datetime

    model_config = {"from_attributes": True}


class SignalStatusUpdate(BaseModel):
    status: str  # reviewed | dismissed
    dismissed_reason: str | None = None


# --- Endpoints ---


@router.get("", response_model=list[SignalResponse])
async def list_signals(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    signal_type: str | None = None,
    status: str | None = None,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get tenant signal feed, paginated."""
    query = select(WwSignal).where(WwSignal.tenant_id == user.tenant_id)

    if signal_type:
        query = query.where(WwSignal.signal_type == signal_type)
    if status:
        query = query.where(WwSignal.status == status)

    query = query.order_by(desc(WwSignal.detected_at))
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/count")
async def signal_count(
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get total signal count for tenant."""
    result = await db.execute(
        select(func.count()).select_from(WwSignal).where(WwSignal.tenant_id == user.tenant_id)
    )
    return {"count": result.scalar() or 0}


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal(
    signal_id: uuid.UUID,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WwSignal).where(
            WwSignal.id == signal_id,
            WwSignal.tenant_id == user.tenant_id,
        )
    )
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal


@router.post("/run")
async def trigger_signal_run(
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger manual signal engine run."""
    from backend.services.signal_engine import run_signal_engine

    result = await run_signal_engine(db, user.tenant_id)
    return result


@router.patch("/{signal_id}/status", response_model=SignalResponse)
async def update_signal_status(
    signal_id: uuid.UUID,
    req: SignalStatusUpdate,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update signal status (reviewed, dismissed)."""
    if req.status not in ("reviewed", "dismissed"):
        raise HTTPException(status_code=400, detail="Status must be 'reviewed' or 'dismissed'")

    result = await db.execute(
        select(WwSignal).where(
            WwSignal.id == signal_id,
            WwSignal.tenant_id == user.tenant_id,
        )
    )
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    values = {"status": req.status, "reviewed_at": datetime.utcnow()}
    if req.dismissed_reason:
        values["dismissed_reason"] = req.dismissed_reason

    await db.execute(
        update(WwSignal).where(WwSignal.id == signal_id).values(**values)
    )
    await db.commit()
    await db.refresh(signal)
    return signal

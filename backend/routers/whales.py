import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.signal import WwSignal
from models.tenant import WwUser
from models.whale import WwWhaleContact, WwWhiteWhale
from routers.auth import get_current_user

router = APIRouter(prefix="/api/whales", tags=["whales"])


# --- Schemas ---


class WhaleCreate(BaseModel):
    company_name: str
    domain: str | None = None
    linkedin_company_url: str | None = None
    why_they_matter: str | None = None
    ideal_entry_point: str | None = None
    internal_notes: str | None = None
    priority_tier: int = 2
    signal_sensitivity: str = "all"


class WhaleUpdate(BaseModel):
    company_name: str | None = None
    domain: str | None = None
    linkedin_company_url: str | None = None
    why_they_matter: str | None = None
    ideal_entry_point: str | None = None
    internal_notes: str | None = None
    status: str | None = None
    priority_tier: int | None = None
    signal_sensitivity: str | None = None


class WhaleResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    company_name: str
    domain: str | None
    linkedin_company_url: str | None
    why_they_matter: str | None
    ideal_entry_point: str | None
    internal_notes: str | None
    status: str
    priority_tier: int
    signal_sensitivity: str
    last_signal_at: datetime | None
    last_contacted_at: datetime | None
    added_at: datetime

    model_config = {"from_attributes": True}


class ContactCreate(BaseModel):
    full_name: str | None = None
    title: str | None = None
    email: str | None = None
    linkedin_url: str | None = None
    is_primary: bool = False


class ContactResponse(BaseModel):
    id: uuid.UUID
    whale_id: uuid.UUID
    full_name: str | None
    title: str | None
    email: str | None
    linkedin_url: str | None
    is_connection: bool
    connection_degree: int | None
    connected_via: str | None
    source: str | None
    is_primary: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Endpoints ---


@router.get("", response_model=list[WhaleResponse])
async def list_whales(
    status: str | None = None,
    tier: int | None = None,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(WwWhiteWhale).where(WwWhiteWhale.tenant_id == user.tenant_id)
    if status:
        query = query.where(WwWhiteWhale.status == status)
    if tier:
        query = query.where(WwWhiteWhale.priority_tier == tier)
    query = query.order_by(WwWhiteWhale.priority_tier, desc(WwWhiteWhale.added_at))

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=WhaleResponse)
async def create_whale(
    req: WhaleCreate,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    whale = WwWhiteWhale(
        tenant_id=user.tenant_id,
        created_by=user.id,
        company_name=req.company_name,
        domain=req.domain,
        linkedin_company_url=req.linkedin_company_url,
        why_they_matter=req.why_they_matter,
        ideal_entry_point=req.ideal_entry_point,
        internal_notes=req.internal_notes,
        priority_tier=req.priority_tier,
        signal_sensitivity=req.signal_sensitivity,
    )
    db.add(whale)
    await db.commit()
    await db.refresh(whale)
    return whale


@router.get("/{whale_id}", response_model=WhaleResponse)
async def get_whale(
    whale_id: uuid.UUID,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WwWhiteWhale).where(
            WwWhiteWhale.id == whale_id,
            WwWhiteWhale.tenant_id == user.tenant_id,
        )
    )
    whale = result.scalar_one_or_none()
    if not whale:
        raise HTTPException(status_code=404, detail="Whale not found")
    return whale


@router.patch("/{whale_id}", response_model=WhaleResponse)
async def update_whale(
    whale_id: uuid.UUID,
    req: WhaleUpdate,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WwWhiteWhale).where(
            WwWhiteWhale.id == whale_id,
            WwWhiteWhale.tenant_id == user.tenant_id,
        )
    )
    whale = result.scalar_one_or_none()
    if not whale:
        raise HTTPException(status_code=404, detail="Whale not found")

    update_data = req.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(WwWhiteWhale).where(WwWhiteWhale.id == whale_id).values(**update_data)
        )
        await db.commit()
        await db.refresh(whale)
    return whale


@router.delete("/{whale_id}")
async def delete_whale(
    whale_id: uuid.UUID,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WwWhiteWhale).where(
            WwWhiteWhale.id == whale_id,
            WwWhiteWhale.tenant_id == user.tenant_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Whale not found")

    await db.execute(delete(WwWhiteWhale).where(WwWhiteWhale.id == whale_id))
    await db.commit()
    return {"status": "deleted"}


@router.get("/{whale_id}/signals")
async def whale_signals(
    whale_id: uuid.UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get signals for a specific whale."""
    result = await db.execute(
        select(WwSignal).where(
            WwSignal.white_whale_id == whale_id,
            WwSignal.tenant_id == user.tenant_id,
        ).order_by(desc(WwSignal.detected_at)).offset((page - 1) * per_page).limit(per_page)
    )
    return result.scalars().all()


@router.get("/{whale_id}/contacts", response_model=list[ContactResponse])
async def list_contacts(
    whale_id: uuid.UUID,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WwWhaleContact).where(WwWhaleContact.whale_id == whale_id)
    )
    return result.scalars().all()


@router.post("/{whale_id}/contacts", response_model=ContactResponse)
async def add_contact(
    whale_id: uuid.UUID,
    req: ContactCreate,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify whale belongs to tenant
    whale_result = await db.execute(
        select(WwWhiteWhale).where(
            WwWhiteWhale.id == whale_id,
            WwWhiteWhale.tenant_id == user.tenant_id,
        )
    )
    if not whale_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Whale not found")

    contact = WwWhaleContact(
        whale_id=whale_id,
        full_name=req.full_name,
        title=req.title,
        email=req.email,
        linkedin_url=req.linkedin_url,
        is_primary=req.is_primary,
        source="manual",
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.post("/{whale_id}/find-contacts")
async def find_contacts(
    whale_id: uuid.UUID,
    user: WwUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger Apollo contact lookup for this whale."""
    from services.contact_finder import find_contacts_for_whale

    result = await db.execute(
        select(WwWhiteWhale).where(
            WwWhiteWhale.id == whale_id,
            WwWhiteWhale.tenant_id == user.tenant_id,
        )
    )
    whale = result.scalar_one_or_none()
    if not whale:
        raise HTTPException(status_code=404, detail="Whale not found")
    if not whale.domain:
        raise HTTPException(status_code=400, detail="Whale has no domain set — needed for contact lookup")

    contacts = await find_contacts_for_whale(db, whale_id, whale.domain)
    return {"found": len(contacts), "contacts": contacts}

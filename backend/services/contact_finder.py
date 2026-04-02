import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.whale import WwWhaleContact
from backend.services.apollo_client import apollo_client


async def find_contacts_for_whale(
    db: AsyncSession,
    whale_id: uuid.UUID,
    company_domain: str,
    titles: list[str] | None = None,
) -> list[dict]:
    """
    Use Apollo to find contacts at a White Whale company.
    Saves results to ww_whale_contacts and returns them.
    """
    if not titles:
        titles = ["CEO", "CRO", "CMO", "VP Sales", "VP Marketing", "VP Revenue", "Head of RevOps"]

    try:
        data = await apollo_client.find_contacts(
            company_domain=company_domain,
            titles=titles,
        )
    except Exception:
        return []

    contacts = []
    for person in data.get("people", []):
        contact = WwWhaleContact(
            whale_id=whale_id,
            full_name=person.get("name"),
            title=person.get("title"),
            email=person.get("email"),
            linkedin_url=person.get("linkedin_url"),
            source="apollo",
        )
        db.add(contact)
        contacts.append({
            "full_name": person.get("name"),
            "title": person.get("title"),
            "email": person.get("email"),
            "linkedin_url": person.get("linkedin_url"),
        })

    await db.commit()
    return contacts

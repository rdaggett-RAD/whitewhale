import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.icp import WwIcpConfig, WwServiceCategory
from models.signal import WwCompany, WwSignal, WwSignalDedup
from models.whale import WwWhiteWhale
from services.apollo_client import apollo_client
from services.classifier import classify_signal, compute_urgency_score
from services.news_client import newsapi_client, serpapi_client


def _fingerprint(signal_type: str, company_domain: str, summary: str) -> str:
    """Generate dedup fingerprint from key signal fields."""
    raw = f"{signal_type}:{company_domain}:{summary[:200]}".lower()
    return hashlib.sha256(raw.encode()).hexdigest()


async def _is_duplicate(db: AsyncSession, tenant_id: uuid.UUID, fingerprint: str) -> bool:
    """Check if signal was already seen within 30-day window."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(WwSignalDedup).where(
            WwSignalDedup.tenant_id == tenant_id,
            WwSignalDedup.signal_fingerprint == fingerprint,
            WwSignalDedup.first_seen_at > cutoff,
        )
    )
    return result.scalar_one_or_none() is not None


async def _record_dedup(
    db: AsyncSession, tenant_id: uuid.UUID, domain: str, signal_type: str, fingerprint: str
) -> None:
    db.add(WwSignalDedup(
        tenant_id=tenant_id,
        company_domain=domain or "",
        signal_type=signal_type,
        signal_fingerprint=fingerprint,
    ))


async def _get_or_create_company(
    db: AsyncSession, tenant_id: uuid.UUID, company_name: str, domain: str | None
) -> WwCompany:
    """Get existing company or create new one."""
    if domain:
        result = await db.execute(
            select(WwCompany).where(
                WwCompany.tenant_id == tenant_id,
                WwCompany.domain == domain,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    company = WwCompany(
        tenant_id=tenant_id,
        company_name=company_name,
        domain=domain,
    )
    db.add(company)
    await db.flush()
    return company


async def _get_service_categories(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    result = await db.execute(
        select(WwServiceCategory).where(
            WwServiceCategory.tenant_id == tenant_id,
            WwServiceCategory.is_active == True,
        )
    )
    categories = result.scalars().all()
    return [{"id": str(c.id), "name": c.name, "description": c.description or ""} for c in categories]


async def _check_whale(db: AsyncSession, tenant_id: uuid.UUID, domain: str | None) -> WwWhiteWhale | None:
    if not domain:
        return None
    result = await db.execute(
        select(WwWhiteWhale).where(
            WwWhiteWhale.tenant_id == tenant_id,
            WwWhiteWhale.domain == domain,
        )
    )
    return result.scalar_one_or_none()


async def collect_job_signals(config: WwIcpConfig) -> list[dict]:
    """Collect job posting signals from Apollo."""
    try:
        data = await apollo_client.search_job_postings(
            industries=config.industries,
            employee_min=config.employee_min,
            employee_max=config.employee_max,
            geos=config.geos,
            keywords=config.keywords_include,
        )
    except Exception:
        return []

    signals = []
    for person in data.get("people", []):
        org = person.get("organization", {})
        company_name = org.get("name", "Unknown")
        domain = org.get("primary_domain")
        title = person.get("title", "")
        signals.append({
            "signal_type": "job_posting",
            "signal_source": "apollo",
            "company_name": company_name,
            "domain": domain,
            "signal_summary": f"{company_name} is hiring: {title}",
            "signal_url": person.get("linkedin_url"),
            "raw_data": person,
        })
    return signals


async def collect_exec_signals(config: WwIcpConfig) -> list[dict]:
    """Collect executive change signals from Apollo."""
    try:
        data = await apollo_client.search_exec_changes(
            industries=config.industries,
            employee_min=config.employee_min,
            employee_max=config.employee_max,
            geos=config.geos,
        )
    except Exception:
        return []

    signals = []
    for person in data.get("people", []):
        org = person.get("organization", {})
        company_name = org.get("name", "Unknown")
        domain = org.get("primary_domain")
        name = person.get("name", "Someone")
        title = person.get("title", "")
        signals.append({
            "signal_type": "exec_change",
            "signal_source": "apollo",
            "company_name": company_name,
            "domain": domain,
            "signal_summary": f"{name} joined {company_name} as {title}",
            "signal_url": person.get("linkedin_url"),
            "raw_data": person,
        })
    return signals


async def collect_news_signals(config: WwIcpConfig) -> list[dict]:
    """Collect news/PR and acquisition signals from NewsAPI + SerpAPI."""
    keywords = config.keywords_include or []
    if not keywords:
        return []

    signals = []

    # NewsAPI
    try:
        articles = await newsapi_client.search_news(keywords)
        for article in articles:
            signals.append({
                "signal_type": "news_pr",
                "signal_source": "newsapi",
                "company_name": article.get("source", {}).get("name", "Unknown"),
                "domain": None,
                "signal_summary": article.get("title", ""),
                "signal_url": article.get("url"),
                "signal_date": article.get("publishedAt"),
                "raw_data": article,
            })
    except Exception:
        pass

    # SerpAPI fallback
    try:
        query = " ".join(keywords[:3]) + " SaaS"
        results = await serpapi_client.search_news(query)
        for item in results:
            signals.append({
                "signal_type": "news_pr",
                "signal_source": "serpapi",
                "company_name": item.get("source", "Unknown"),
                "domain": None,
                "signal_summary": item.get("title", ""),
                "signal_url": item.get("link"),
                "raw_data": item,
            })
    except Exception:
        pass

    return signals


async def collect_funding_signals(config: WwIcpConfig) -> list[dict]:
    """Collect funding signals from NewsAPI + SerpAPI."""
    keywords = config.keywords_include or []
    signals = []

    try:
        articles = await newsapi_client.search_funding(keywords)
        for article in articles:
            signals.append({
                "signal_type": "funding",
                "signal_source": "newsapi",
                "company_name": article.get("source", {}).get("name", "Unknown"),
                "domain": None,
                "signal_summary": article.get("title", ""),
                "signal_url": article.get("url"),
                "signal_date": article.get("publishedAt"),
                "raw_data": article,
            })
    except Exception:
        pass

    if keywords:
        try:
            results = await serpapi_client.search_funding(keywords)
            for item in results:
                signals.append({
                    "signal_type": "funding",
                    "signal_source": "serpapi",
                    "company_name": item.get("source", "Unknown"),
                    "domain": None,
                    "signal_summary": item.get("title", ""),
                    "signal_url": item.get("link"),
                    "raw_data": item,
                })
        except Exception:
            pass

    return signals


async def run_whale_sweep(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    """Run targeted signal sweep for White Whale companies."""
    result = await db.execute(
        select(WwWhiteWhale).where(
            WwWhiteWhale.tenant_id == tenant_id,
            WwWhiteWhale.status.in_(["cold", "warming", "active"]),
        )
    )
    whales = result.scalars().all()
    signals = []

    for whale in whales:
        if not whale.domain:
            continue
        # Search news about this specific company
        try:
            articles = await newsapi_client.search_news([whale.company_name], days_back=7, page_size=5)
            for article in articles:
                signals.append({
                    "signal_type": "news_pr",
                    "signal_source": "newsapi",
                    "company_name": whale.company_name,
                    "domain": whale.domain,
                    "signal_summary": article.get("title", ""),
                    "signal_url": article.get("url"),
                    "signal_date": article.get("publishedAt"),
                    "raw_data": article,
                    "white_whale_id": whale.id,
                })
        except Exception:
            pass

    return signals


async def run_signal_engine(db: AsyncSession, tenant_id: uuid.UUID) -> dict:
    """
    Main signal engine orchestrator.
    Collects signals, deduplicates, classifies, and saves.
    Returns summary stats.
    """
    # Get ICP config
    result = await db.execute(
        select(WwIcpConfig).where(
            WwIcpConfig.tenant_id == tenant_id,
            WwIcpConfig.is_active == True,
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        return {"error": "No active ICP config found", "processed": 0, "saved": 0}

    # Get service categories for classification
    categories = await _get_service_categories(db, tenant_id)

    # Collect signals from all sources
    raw_signals = []

    if config.watch_job_postings:
        raw_signals += await collect_job_signals(config)

    if config.watch_exec_changes:
        raw_signals += await collect_exec_signals(config)

    if config.watch_news_pr or config.watch_acquisitions:
        raw_signals += await collect_news_signals(config)

    if config.watch_funding:
        raw_signals += await collect_funding_signals(config)

    # Whale-specific sweep
    whale_signals = await run_whale_sweep(db, tenant_id)
    raw_signals += whale_signals

    # Process each signal
    saved_count = 0
    skipped_count = 0

    for raw in raw_signals:
        domain = raw.get("domain", "") or ""
        fp = _fingerprint(raw["signal_type"], domain, raw.get("signal_summary", ""))

        # Dedup
        if await _is_duplicate(db, tenant_id, fp):
            skipped_count += 1
            continue

        # Classify
        classification = await classify_signal(
            signal_summary=raw.get("signal_summary", ""),
            signal_type=raw["signal_type"],
            company_name=raw.get("company_name", "Unknown"),
            service_categories=categories,
        )

        if classification["confidence"] < config.min_signal_score:
            skipped_count += 1
            continue

        # Get or create company
        company = await _get_or_create_company(
            db, tenant_id, raw.get("company_name", "Unknown"), domain
        )

        # Check if this is a whale
        whale = await _check_whale(db, tenant_id, domain)
        whale_id = raw.get("white_whale_id") or (whale.id if whale else None)

        # Compute urgency
        urgency = compute_urgency_score(
            signal_age_hours=0,  # fresh signal
            is_tier1_whale=whale.priority_tier == 1 if whale else False,
        )

        # Save signal
        signal = WwSignal(
            tenant_id=tenant_id,
            company_id=company.id,
            white_whale_id=whale_id,
            signal_type=raw["signal_type"],
            signal_source=raw.get("signal_source"),
            raw_data=raw.get("raw_data"),
            signal_summary=raw.get("signal_summary", ""),
            signal_url=raw.get("signal_url"),
            service_category_id=classification["service_category_id"],
            classification_confidence=classification["confidence"],
            classification_rationale=classification["rationale"],
            urgency_score=urgency,
        )
        db.add(signal)

        # Record dedup
        await _record_dedup(db, tenant_id, domain, raw["signal_type"], fp)

        # Update whale last_signal_at
        if whale:
            whale.last_signal_at = datetime.now(timezone.utc)

        saved_count += 1

    await db.commit()

    return {
        "processed": len(raw_signals),
        "saved": saved_count,
        "skipped": skipped_count,
    }

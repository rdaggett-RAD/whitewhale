import json
import uuid

import httpx

from backend.config import settings

CLAUDE_MODEL = "claude-sonnet-4-20250514"


async def classify_signal(
    signal_summary: str,
    signal_type: str,
    company_name: str,
    service_categories: list[dict],
) -> dict:
    """
    Classify a signal against tenant's service categories using Claude.

    Returns:
        {
            "service_category_id": uuid | None,
            "confidence": int (0-100),
            "rationale": str
        }
    """
    if not settings.ANTHROPIC_API_KEY:
        return {"service_category_id": None, "confidence": 0, "rationale": "Anthropic API key not configured"}

    categories_text = "\n".join(
        f"- {cat['name']} (ID: {cat['id']}): {cat['description']}"
        for cat in service_categories
    )

    system_prompt = """You are a signal classifier for a B2B services company.
Given a business signal and a list of service categories, determine which category (if any) the signal best maps to.

Return ONLY valid JSON with this exact structure:
{"service_category_id": "uuid-string-or-null", "confidence": 0-100, "rationale": "one sentence"}

If no category fits, set service_category_id to null and confidence to 0."""

    user_prompt = f"""SIGNAL TYPE: {signal_type}
COMPANY: {company_name}
SIGNAL: {signal_summary}

SERVICE CATEGORIES:
{categories_text}

Classify this signal."""

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 200,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
        )
        resp.raise_for_status()
        data = resp.json()

    text = data["content"][0]["text"].strip()

    try:
        result = json.loads(text)
        cat_id = result.get("service_category_id")
        return {
            "service_category_id": uuid.UUID(cat_id) if cat_id else None,
            "confidence": int(result.get("confidence", 0)),
            "rationale": result.get("rationale", ""),
        }
    except (json.JSONDecodeError, ValueError):
        return {"service_category_id": None, "confidence": 0, "rationale": f"Failed to parse: {text[:100]}"}


def compute_urgency_score(
    signal_age_hours: float,
    is_tier1_whale: bool = False,
    has_connection: bool = False,
    contacted_in_30d: bool = False,
) -> int:
    """Compute urgency score based on spec rules."""
    score = 50  # base

    if is_tier1_whale:
        score += 30
    if signal_age_hours < 6:
        score += 20
    if has_connection:
        score += 25
    if signal_age_hours > 48:
        score -= 20
    if contacted_in_30d:
        score -= 40

    return max(0, min(100, score))

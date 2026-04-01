import httpx

from backend.config import settings
from backend.database import engine


async def check_database() -> dict:
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"name": "Database", "status": "connected", "detail": "PostgreSQL responding"}
    except Exception as e:
        return {"name": "Database", "status": "error", "detail": str(e)[:200]}


async def check_redis() -> dict:
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
        return {"name": "Redis", "status": "connected", "detail": "Redis responding"}
    except Exception as e:
        return {"name": "Redis", "status": "error", "detail": str(e)[:200]}


async def check_anthropic() -> dict:
    if not settings.ANTHROPIC_API_KEY:
        return {"name": "Anthropic", "status": "not_configured", "detail": "ANTHROPIC_API_KEY not set"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "ping"}],
                },
                timeout=10,
            )
            if resp.status_code in (200, 201):
                return {"name": "Anthropic", "status": "connected", "detail": "Claude API responding"}
            return {"name": "Anthropic", "status": "error", "detail": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"name": "Anthropic", "status": "error", "detail": str(e)[:200]}


async def check_apollo() -> dict:
    if not settings.APOLLO_API_KEY:
        return {"name": "Apollo", "status": "not_configured", "detail": "APOLLO_API_KEY not set"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.apollo.io/v1/auth/health",
                headers={"Content-Type": "application/json"},
                json={"api_key": settings.APOLLO_API_KEY},
                timeout=10,
            )
            if resp.status_code == 200:
                return {"name": "Apollo", "status": "connected", "detail": "Apollo API responding"}
            return {"name": "Apollo", "status": "error", "detail": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"name": "Apollo", "status": "error", "detail": str(e)[:200]}


async def check_newsapi() -> dict:
    if not settings.NEWSAPI_KEY:
        return {"name": "NewsAPI", "status": "not_configured", "detail": "NEWSAPI_KEY not set"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://newsapi.org/v2/top-headlines",
                params={"apiKey": settings.NEWSAPI_KEY, "pageSize": 1, "country": "us"},
                timeout=10,
            )
            if resp.status_code == 200:
                return {"name": "NewsAPI", "status": "connected", "detail": "NewsAPI responding"}
            return {"name": "NewsAPI", "status": "error", "detail": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"name": "NewsAPI", "status": "error", "detail": str(e)[:200]}


async def check_serpapi() -> dict:
    if not settings.SERPAPI_KEY:
        return {"name": "SerpAPI", "status": "not_configured", "detail": "SERPAPI_KEY not set"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://serpapi.com/account.json",
                params={"api_key": settings.SERPAPI_KEY},
                timeout=10,
            )
            if resp.status_code == 200:
                return {"name": "SerpAPI", "status": "connected", "detail": "SerpAPI responding"}
            return {"name": "SerpAPI", "status": "error", "detail": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"name": "SerpAPI", "status": "error", "detail": str(e)[:200]}


async def check_unipile() -> dict:
    if not settings.UNIPILE_API_KEY or not settings.UNIPILE_DSN:
        return {"name": "Unipile", "status": "not_configured", "detail": "UNIPILE_API_KEY or UNIPILE_DSN not set"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.UNIPILE_DSN}/api/v1/accounts",
                headers={"X-API-KEY": settings.UNIPILE_API_KEY},
                timeout=10,
            )
            if resp.status_code == 200:
                return {"name": "Unipile", "status": "connected", "detail": "Unipile API responding"}
            return {"name": "Unipile", "status": "error", "detail": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"name": "Unipile", "status": "error", "detail": str(e)[:200]}


async def check_resend() -> dict:
    if not settings.RESEND_API_KEY:
        return {"name": "Resend", "status": "not_configured", "detail": "RESEND_API_KEY not set"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.resend.com/api-keys",
                headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                timeout=10,
            )
            if resp.status_code == 200:
                return {"name": "Resend", "status": "connected", "detail": "Resend API responding"}
            return {"name": "Resend", "status": "error", "detail": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"name": "Resend", "status": "error", "detail": str(e)[:200]}


async def check_all_integrations() -> list[dict]:
    import asyncio

    results = await asyncio.gather(
        check_database(),
        check_redis(),
        check_anthropic(),
        check_apollo(),
        check_newsapi(),
        check_serpapi(),
        check_unipile(),
        check_resend(),
    )
    return list(results)

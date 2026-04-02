import httpx

from config import settings


class NewsAPIClient:
    BASE_URL = "https://newsapi.org/v2"

    def __init__(self):
        self.api_key = settings.NEWSAPI_KEY

    async def search_news(
        self,
        keywords: list[str],
        days_back: int = 7,
        page_size: int = 20,
    ) -> list[dict]:
        """Search for news articles matching keywords."""
        from datetime import datetime, timedelta, timezone

        query = " OR ".join(f'"{kw}"' for kw in keywords[:5])
        from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.BASE_URL}/everything",
                params={
                    "apiKey": self.api_key,
                    "q": query,
                    "from": from_date,
                    "sortBy": "publishedAt",
                    "pageSize": page_size,
                    "language": "en",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("articles", [])

    async def search_funding(
        self,
        keywords: list[str] | None = None,
        days_back: int = 7,
        page_size: int = 20,
    ) -> list[dict]:
        """Search for funding/investment news."""
        base_terms = ["funding round", "Series A", "Series B", "Series C", "raised", "investment"]
        if keywords:
            base_terms = [f"{kw} {term}" for kw in keywords[:3] for term in ["funding", "raised", "investment"]]
        return await self.search_news(base_terms[:5], days_back, page_size)

    async def search_acquisitions(
        self,
        keywords: list[str] | None = None,
        days_back: int = 7,
        page_size: int = 20,
    ) -> list[dict]:
        """Search for acquisition/merger news."""
        base_terms = ["acquired", "acquisition", "merger", "acquires"]
        if keywords:
            base_terms = [f"{kw} {term}" for kw in keywords[:3] for term in ["acquired", "acquisition"]]
        return await self.search_news(base_terms[:5], days_back, page_size)


class SerpAPIClient:
    BASE_URL = "https://serpapi.com/search.json"

    def __init__(self):
        self.api_key = settings.SERPAPI_KEY

    async def search_news(
        self,
        query: str,
        num_results: int = 10,
    ) -> list[dict]:
        """Search Google News via SerpAPI."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                self.BASE_URL,
                params={
                    "api_key": self.api_key,
                    "q": query,
                    "tbm": "nws",
                    "num": num_results,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("news_results", [])

    async def search_funding(self, keywords: list[str]) -> list[dict]:
        """Search for funding news via SerpAPI."""
        query = " ".join(keywords[:3]) + " funding OR raised OR investment"
        return await self.search_news(query)

    async def search_acquisitions(self, keywords: list[str]) -> list[dict]:
        """Search for acquisition news via SerpAPI."""
        query = " ".join(keywords[:3]) + " acquired OR acquisition OR merger"
        return await self.search_news(query)


newsapi_client = NewsAPIClient()
serpapi_client = SerpAPIClient()

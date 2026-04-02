import httpx

from backend.config import settings


class ApolloClient:
    BASE_URL = "https://api.apollo.io/v1"

    def __init__(self):
        self.api_key = settings.APOLLO_API_KEY

    def _headers(self) -> dict:
        return {"Content-Type": "application/json"}

    def _body(self, **kwargs) -> dict:
        return {"api_key": self.api_key, **kwargs}

    async def search_job_postings(
        self,
        industries: list[str] | None = None,
        employee_min: int | None = None,
        employee_max: int | None = None,
        geos: list[str] | None = None,
        keywords: list[str] | None = None,
        page: int = 1,
        per_page: int = 25,
    ) -> dict:
        """Search for companies with relevant job postings matching ICP filters."""
        params = {}
        if industries:
            params["organization_industry_tag_ids"] = industries
        if employee_min or employee_max:
            ranges = []
            lo = employee_min or 1
            hi = employee_max or 100000
            ranges.append(f"{lo},{hi}")
            params["organization_num_employees_ranges"] = ranges
        if geos:
            params["person_locations"] = geos
        if keywords:
            params["q_organization_keyword_tags"] = keywords

        # Search for people with GTM/RevOps titles at matching companies
        params["person_titles"] = [
            "RevOps", "Revenue Operations", "VP Sales", "CRO", "CMO",
            "VP Marketing", "Head of Marketing", "ABM", "Demand Gen",
            "VP Revenue", "Head of RevOps", "GTM",
        ]
        params["page"] = page
        params["per_page"] = per_page

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.BASE_URL}/mixed_people/search",
                headers=self._headers(),
                json=self._body(**params),
            )
            resp.raise_for_status()
            return resp.json()

    async def search_exec_changes(
        self,
        industries: list[str] | None = None,
        employee_min: int | None = None,
        employee_max: int | None = None,
        geos: list[str] | None = None,
        page: int = 1,
        per_page: int = 25,
    ) -> dict:
        """Search for executives who recently changed jobs into ICP companies."""
        params = {
            "person_titles": [
                "CRO", "VP Sales", "CMO", "VP Revenue", "Head of RevOps",
                "VP Marketing", "Chief Marketing Officer", "Chief Revenue Officer",
            ],
            "person_changed_job_within_last_90_days": True,
            "page": page,
            "per_page": per_page,
        }
        if industries:
            params["organization_industry_tag_ids"] = industries
        if employee_min or employee_max:
            lo = employee_min or 1
            hi = employee_max or 100000
            params["organization_num_employees_ranges"] = [f"{lo},{hi}"]
        if geos:
            params["person_locations"] = geos

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.BASE_URL}/mixed_people/search",
                headers=self._headers(),
                json=self._body(**params),
            )
            resp.raise_for_status()
            return resp.json()

    async def search_company(self, domain: str) -> dict | None:
        """Look up a single company by domain."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.BASE_URL}/organizations/enrich",
                headers=self._headers(),
                json=self._body(domain=domain),
            )
            if resp.status_code == 200:
                return resp.json().get("organization")
            return None

    async def find_contacts(
        self,
        company_domain: str,
        titles: list[str] | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> dict:
        """Find contacts at a specific company by title."""
        params = {
            "q_organization_domains": company_domain,
            "page": page,
            "per_page": per_page,
        }
        if titles:
            params["person_titles"] = titles

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.BASE_URL}/mixed_people/search",
                headers=self._headers(),
                json=self._body(**params),
            )
            resp.raise_for_status()
            return resp.json()


apollo_client = ApolloClient()

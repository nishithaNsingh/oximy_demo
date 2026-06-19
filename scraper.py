import httpx
from bs4 import BeautifulSoup

from config import (
    PRIVACY_PAGE_PATHS,
    SCRAPER_MAX_CHARS_PER_PAGE,
    SCRAPER_TIMEOUT_SECONDS,
)


async def scrape_domain(domain: str) -> dict[str, str]:
    """
    Fetches text content from known privacy/security page paths on a domain.

    Returns a dict mapping URL → extracted text. Empty dict means no pages
    were reachable.
    """
    urls = [f"https://{domain}{path}" for path in PRIVACY_PAGE_PATHS]
    pages: dict[str, str] = {}

    async with httpx.AsyncClient(timeout=SCRAPER_TIMEOUT_SECONDS,headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    },
    follow_redirects=True,) as client:
        for url in urls:
            try:
                response = await client.get(url, follow_redirects=True)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()

                text = soup.get_text(separator=" ", strip=True)
                if text:
                    pages[url] = text[:SCRAPER_MAX_CHARS_PER_PAGE]

            except Exception as exc:
                print(f"[scraper] Failed to fetch {url}: {exc}")

    return pages
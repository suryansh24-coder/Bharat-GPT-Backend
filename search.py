import httpx
from app.config import settings
from app.utils.logger import logger

async def perform_web_search(query: str):
    """
    Zero Hallucination Protocol Search via SerpAPI.
    """
    if not settings.SERPAPI_KEY or settings.SERPAPI_KEY == "dummy_key":
        logger.warning("SerpAPI key not set. Returning mock data.")
        return [{
            "title": "Mock Result for " + query,
            "link": "https://example.com/mock",
            "snippet": "This is a mock snippet because SERPAPI_KEY is not configured. Configure it in production."
        }]
        
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                "https://serpapi.com/search.json",
                params={
                    "q": query,
                    "engine": "google",
                    "api_key": settings.SERPAPI_KEY,
                    "num": 5
                },
                timeout=5.0
            )
            res.raise_for_status()
            data = res.json()
            
            organic = data.get("organic_results", [])
            results = []
            for item in organic[:5]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet", "No description available.")
                })
            return results
    except Exception as e:
        logger.error(f"Search API Error: {str(e)}")
        raise e

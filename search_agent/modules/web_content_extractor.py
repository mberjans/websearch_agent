
import httpx
from bs4 import BeautifulSoup
from typing import Optional

from search_agent.core.exceptions import ScrapingError

async def extract_main_content(url: str) -> Optional[str]:
    """
    Fetches the content of a URL and extracts the main textual content.
    Uses httpx for fetching and BeautifulSoup for parsing.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find common elements that contain main content
        main_content_elements = soup.find_all(['article', 'main', 'div'], class_=['content', 'main-content', 'post-content', 'article-body'])

        if not main_content_elements:
            # Fallback to body if no specific content elements are found
            main_content_elements = [soup.body] if soup.body else []

        if not main_content_elements:
            return None

        # Extract text and clean it
        texts = []
        for element in main_content_elements:
            for script_or_style in element(['script', 'style']):
                script_or_style.extract() # Remove script and style tags
            texts.append(element.get_text(separator=' ', strip=True))

        cleaned_text = " ".join(texts)
        return cleaned_text if cleaned_text else None

    except httpx.RequestError as e:
        raise ScrapingError(f"Network or HTTP error while fetching {url}: {e}")
    except Exception as e:
        raise ScrapingError(f"Error extracting content from {url}: {e}")

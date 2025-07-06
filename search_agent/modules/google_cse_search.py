"""Google Custom Search Engine API module.

This module implements web search functionality using the Google Custom Search Engine (CSE) API
to provide high-quality search results from Google's search infrastructure.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import List

import typer
import httpx
from search_agent.core.models import SearchResult, SearchModuleOutput
from search_agent.core.exceptions import ScrapingError, NoResultsError, ConfigurationError
from search_agent.config import settings

# The Typer app instance
app = typer.Typer()


async def search(query: str) -> SearchModuleOutput:
    """
    The core library function that performs the search using Google Custom Search Engine API.
    This function contains the main logic and is what other parts of the system will import and call.
    """
    start_time = time.perf_counter()
    
    # Check if API key and CSE ID are configured
    if not settings.GOOGLE_API_KEY:
        raise ConfigurationError("GOOGLE_API_KEY is not configured in settings")
    
    if not settings.GOOGLE_CSE_ID:
        raise ConfigurationError("GOOGLE_CSE_ID is not configured in settings")
    
    # Google Custom Search API endpoint
    api_url = "https://www.googleapis.com/customsearch/v1"
    
    # Request parameters
    params = {
        "key": settings.GOOGLE_API_KEY,
        "cx": settings.GOOGLE_CSE_ID,
        "q": query,
        "num": 10,  # Number of results to return (max 10 per request)
        "start": 1,  # Starting index (1-based)
        "safe": "medium",  # Safe search setting
        "lr": "lang_en",  # Language restriction
        "gl": "us",  # Geolocation
        "hl": "en"  # Interface language
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, params=params)
            
            # Check for API errors
            if response.status_code == 400:
                raise ConfigurationError("Invalid Google CSE API request parameters")
            elif response.status_code == 403:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_reason = error_data.get("error", {}).get("errors", [{}])[0].get("reason", "unknown")
                
                if error_reason == "keyInvalid":
                    raise ConfigurationError("Invalid Google API key")
                elif error_reason == "dailyLimitExceeded":
                    raise ScrapingError("Google CSE API daily quota exceeded")
                elif error_reason == "quotaExceeded":
                    raise ScrapingError("Google CSE API quota exceeded")
                else:
                    raise ConfigurationError(f"Google CSE API access denied: {error_reason}")
            elif response.status_code == 429:
                raise ScrapingError("Google CSE API rate limit exceeded")
            elif response.status_code != 200:
                raise ScrapingError(f"Google CSE API returned status code {response.status_code}: {response.text}")
            
            # Parse JSON response
            data = response.json()
            
            # Extract search results
            scraped_results = []
            
            # Check if we have search results
            if "items" in data:
                items = data["items"]
                
                for item in items:
                    try:
                        # Extract required fields
                        title = item.get("title", "").strip()
                        url = item.get("link", "").strip()
                        snippet = item.get("snippet", "").strip()
                        
                        # Only add result if we have title and URL
                        if title and url:
                            scraped_results.append(SearchResult(
                                title=title,
                                url=url,
                                snippet=snippet if snippet else "No snippet available"
                            ))
                    except Exception as e:
                        # Skip individual result if parsing fails
                        continue
            
            # Check if we got any results
            if not scraped_results:
                # Check if there's an error message in the response
                if "error" in data:
                    error_msg = data["error"].get("message", "Unknown API error")
                    raise ScrapingError(f"Google CSE API error: {error_msg}")
                else:
                    # Check search information
                    search_info = data.get("searchInformation", {})
                    total_results = search_info.get("totalResults", "0")
                    
                    if total_results == "0":
                        raise NoResultsError(f"No search results found for query: {query}")
                    else:
                        raise ScrapingError("Google CSE API returned no items despite indicating results exist")
                    
    except httpx.TimeoutException:
        raise ScrapingError("Google CSE API request timed out")
    except httpx.RequestError as e:
        raise ScrapingError(f"Google CSE API request failed: {e}")
    except Exception as e:
        if isinstance(e, (ConfigurationError, ScrapingError, NoResultsError)):
            raise
        else:
            raise ScrapingError(f"Unexpected error during Google CSE API search: {e}")
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return SearchModuleOutput(
        source_name="google_cse_search",
        query=query,
        timestamp_utc=datetime.now(timezone.utc),
        execution_time_seconds=execution_time,
        results=scraped_results
    )


@app.command()
def main(
    query: str = typer.Option(
        ...,
        "--query",
        "-q",
        help="The search query to execute."
    )
):
    """
    The CLI entry point. This function is a thin wrapper around the async `search` function.
    It handles CLI argument parsing and prints the standardized JSON output.
    """
    try:
        result_obj = asyncio.run(search(query))
        # Pydantic's model_dump_json method ensures standardized, validated JSON output.
        print(result_obj.model_dump_json(indent=2))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    # This block makes the script executable from the command line.
    app()
"""Brave Search API module.

This module implements web search functionality using the Brave Search API
to provide fast, reliable search results from a commercial search service.
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
    The core library function that performs the search using Brave Search API.
    This function contains the main logic and is what other parts of the system will import and call.
    """
    start_time = time.perf_counter()
    
    # Check if API key is configured
    if not settings.BRAVE_API_KEY:
        raise ConfigurationError("BRAVE_API_KEY is not configured in settings")
    
    # Brave Search API endpoint
    api_url = "https://api.search.brave.com/res/v1/web/search"
    
    # Request parameters
    params = {
        "q": query,
        "count": 10,  # Number of results to return
        "offset": 0,  # Starting offset
        "mkt": "en-US",  # Market/locale
        "safesearch": "moderate",  # Safe search setting
        "freshness": "",  # No freshness filter
        "text_decorations": False,  # Don't include text decorations
        "spellcheck": True  # Enable spell checking
    }
    
    # Request headers
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": settings.BRAVE_API_KEY
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, params=params, headers=headers)
            
            # Check for API errors
            if response.status_code == 401:
                raise ConfigurationError("Invalid Brave API key")
            elif response.status_code == 429:
                raise ScrapingError("Brave API rate limit exceeded")
            elif response.status_code != 200:
                raise ScrapingError(f"Brave API returned status code {response.status_code}: {response.text}")
            
            # Parse JSON response
            data = response.json()
            
            # Extract search results
            scraped_results = []
            
            # Check if we have web results
            if "web" in data and "results" in data["web"]:
                web_results = data["web"]["results"]
                
                for result in web_results:
                    try:
                        # Extract required fields
                        title = result.get("title", "").strip()
                        url = result.get("url", "").strip()
                        description = result.get("description", "").strip()
                        
                        # Only add result if we have title and URL
                        if title and url:
                            scraped_results.append(SearchResult(
                                title=title,
                                url=url,
                                snippet=description if description else "No description available"
                            ))
                    except Exception as e:
                        # Skip individual result if parsing fails
                        continue
            
            # Check if we got any results
            if not scraped_results:
                # Check if there's an error message in the response
                if "error" in data:
                    error_msg = data["error"].get("message", "Unknown API error")
                    raise ScrapingError(f"Brave API error: {error_msg}")
                else:
                    raise NoResultsError(f"No search results found for query: {query}")
                    
    except httpx.TimeoutException:
        raise ScrapingError("Brave API request timed out")
    except httpx.RequestError as e:
        raise ScrapingError(f"Brave API request failed: {e}")
    except Exception as e:
        if isinstance(e, (ConfigurationError, ScrapingError, NoResultsError)):
            raise
        else:
            raise ScrapingError(f"Unexpected error during Brave API search: {e}")
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return SearchModuleOutput(
        source_name="brave_api_search",
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
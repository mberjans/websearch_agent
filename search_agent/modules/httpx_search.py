"""httpx + BeautifulSoup search module.

This module implements web search functionality using httpx for HTTP requests
and BeautifulSoup for HTML parsing. It's designed for fast scraping of simple,
static HTML search engines that don't rely heavily on JavaScript.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import List
from urllib.parse import urljoin, urlparse

import typer
import httpx
from bs4 import BeautifulSoup
from search_agent.core.models import SearchResult, SearchModuleOutput
from search_agent.core.exceptions import ScrapingError, NoResultsError

# The Typer app instance
app = typer.Typer()


async def search(query: str) -> SearchModuleOutput:
    """
    The core library function that performs the search using httpx + BeautifulSoup.
    This function contains the main logic and is what other parts of the system will import and call.
    """
    start_time = time.perf_counter()
    
    # Use DuckDuckGo as the target search engine (simple HTML version)
    base_url = "https://html.duckduckgo.com/html/"
    
    # Request parameters
    params = {
        "q": query,
        "kl": "us-en",  # Region/language
        "s": "0",       # Start index
        "dc": "10",     # Number of results per page
        "v": "l",       # Layout version
        "o": "json",    # Output format preference
        "api": "/d.js"  # API endpoint
    }
    
    # Headers to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers=headers
        ) as client:
            
            # Make the search request
            response = await client.get(base_url, params=params)
            
            # Check response status
            if response.status_code != 200:
                raise ScrapingError(f"HTTP request failed with status code {response.status_code}")
            
            # Parse HTML content with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results using CSS selectors
            scraped_results = []
            
            # DuckDuckGo HTML version uses specific CSS classes
            result_containers = soup.select('.result')
            
            if not result_containers:
                # Try alternative selectors
                result_containers = soup.select('.web-result')
                
            if not result_containers:
                # Try even more generic selectors
                result_containers = soup.select('.result__body')
            
            for container in result_containers:
                try:
                    # Extract title and URL
                    title_element = container.select_one('.result__title a, .result-title a, h2 a, h3 a')
                    if not title_element:
                        continue
                    
                    title = title_element.get_text(strip=True)
                    url = title_element.get('href', '')
                    
                    # Handle relative URLs
                    if url.startswith('/'):
                        url = urljoin(base_url, url)
                    elif url.startswith('//'):
                        url = 'https:' + url
                    
                    # Extract snippet/description
                    snippet_element = container.select_one('.result__snippet, .result-snippet, .snippet')
                    snippet = ""
                    if snippet_element:
                        snippet = snippet_element.get_text(strip=True)
                    
                    # Use fallback snippet if none found
                    if not snippet:
                        snippet = "No snippet available"
                    
                    # Only add result if we have title and URL
                    if title and url and not url.startswith('#'):
                        # Clean up the URL if it's a DuckDuckGo redirect
                        if 'duckduckgo.com' in url and '/l/?uddg=' in url:
                            # Extract the actual URL from DuckDuckGo's redirect
                            import urllib.parse
                            parsed = urllib.parse.urlparse(url)
                            query_params = urllib.parse.parse_qs(parsed.query)
                            if 'uddg' in query_params:
                                url = urllib.parse.unquote(query_params['uddg'][0])
                        
                        scraped_results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet
                        ))
                        
                except Exception as e:
                    # Skip individual result if parsing fails
                    continue
            
            # Check if we got any results
            if not scraped_results:
                # Check if the page indicates no results
                no_results_indicators = [
                    "No results found",
                    "no results",
                    "0 results",
                    "Try different keywords"
                ]
                
                page_text = soup.get_text().lower()
                if any(indicator in page_text for indicator in no_results_indicators):
                    raise NoResultsError(f"No search results found for query: {query}")
                else:
                    # Might be a parsing issue or blocked
                    raise ScrapingError("Could not parse search results from the page")
                    
    except httpx.TimeoutException:
        raise ScrapingError("HTTP request timed out")
    except httpx.RequestError as e:
        raise ScrapingError(f"HTTP request failed: {e}")
    except Exception as e:
        if isinstance(e, (ScrapingError, NoResultsError)):
            raise
        else:
            raise ScrapingError(f"Unexpected error during httpx search: {e}")
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return SearchModuleOutput(
        source_name="httpx_search",
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
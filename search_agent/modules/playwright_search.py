"""Playwright-based web search module.

This module implements web search functionality using Playwright to scrape
search results from DuckDuckGo in a headless browser environment with async capabilities.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING

import typer
from playwright.async_api import async_playwright, Browser, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

if TYPE_CHECKING:
    from search_agent.config import Configuration

from search_agent.core.models import SearchResult, SearchModuleOutput
from search_agent.core.exceptions import ScrapingError, NoResultsError

# The Typer app instance
app = typer.Typer()


async def search(query: str, config: Optional['Configuration'] = None) -> SearchModuleOutput:
    """
    The core library function that performs the search using Playwright.
    This function contains the main logic and is what other parts of the system will import and call.
    
    Args:
        query: The search query to execute
        config: Optional configuration object for search parameters
        
    Returns:
        SearchModuleOutput containing search results
    """
    start_time = time.perf_counter()
    
    # Get configuration parameters
    timeout_ms = 10000  # Reduced default timeout from 30s to 10s
    user_agent = None
    proxy = None
    
    if config:
        if hasattr(config, 'search') and config.search.timeout:
            timeout_ms = config.search.timeout * 1000  # Convert to milliseconds
        if hasattr(config, 'advanced'):
            if config.advanced.user_agent:
                user_agent = config.advanced.user_agent
            if config.advanced.proxy:
                proxy = config.advanced.proxy
    
    async with async_playwright() as p:
        browser = None
        try:
            # Configure browser launch options
            launch_options = {"headless": True}
            if proxy:
                launch_options["proxy"] = {"server": proxy}
            
            browser = await p.chromium.launch(**launch_options)
            
            # Configure page options
            page_options = {}
            if user_agent:
                page_options["user_agent"] = user_agent
                
            page = await browser.new_page(**page_options)
            
            await page.goto(f"https://duckduckgo.com/?q={query}&t=h_&ia=web")
            
            await page.wait_for_selector("[data-testid='result']", timeout=timeout_ms)
            
            result_elements = await (await page.locator("[data-testid='result']")).all()
            
            if not result_elements:
                raise NoResultsError(f"No search results found for query: {query}")

            scraped_results = []
            for result_element in result_elements:
                title_element = (await result_element.locator("[data-testid='result-title-a']")).first
                snippet_element = (await result_element.locator("[data-testid='result-snippet']")).first
                
                title = str(await title_element.inner_text())
                url = str(await title_element.get_attribute('href'))
                snippet = str(await snippet_element.inner_text())
                
                if title and url:
                    scraped_results.append(SearchResult(title=title, url=url, snippet=snippet))

            if not scraped_results:
                raise NoResultsError(f"No valid search results could be parsed for query: {query}")

            return SearchModuleOutput(
                source_name="playwright_search",
                query=query,
                timestamp_utc=datetime.now(timezone.utc),
                execution_time_seconds=time.perf_counter() - start_time,
                results=scraped_results
            )

        except PlaywrightTimeoutError as e:
            raise ScrapingError(f"Playwright timeout error: {e}")
        except Exception as e:
            raise ScrapingError(f"Unexpected error during search: {e}")
        finally:
            if browser:
                await browser.close()


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
        print(result_obj.model_dump_json(indent=2))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
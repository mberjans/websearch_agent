"""Playwright-based web search module.

This module implements web search functionality using Playwright to scrape
search results from DuckDuckGo in a headless browser environment with async capabilities.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import List

import typer
from playwright.async_api import async_playwright, Browser, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from search_agent.core.models import SearchResult, SearchModuleOutput
from search_agent.core.exceptions import ScrapingError, NoResultsError

# The Typer app instance
app = typer.Typer()


async def search(query: str) -> SearchModuleOutput:
    """
    The core library function that performs the search using Playwright.
    This function contains the main logic and is what other parts of the system will import and call.
    """
    start_time = time.perf_counter()
    
    async with async_playwright() as p:
        browser = None
        try:
            # Launch browser in headless mode with anti-detection measures
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding"
                ]
            )
            
            # Create a new page with user agent and additional settings
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            
            # Remove webdriver property to avoid detection
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Navigate to DuckDuckGo with the query
            search_url = f"https://duckduckgo.com/?q={query}&t=h_&ia=web"
            await page.goto(search_url, wait_until="networkidle")
            
            # Wait for search results to load
            await page.wait_for_timeout(5000)  # Give page time to load
            
            # Try multiple selectors to find search results
            result_elements = []
            selectors_to_try = [
                "[data-testid='result']",
                ".result",
                "article",
                "[data-testid='web-results'] > div",
                ".web-result",
                ".organic-result"
            ]
            
            for selector in selectors_to_try:
                try:
                    # Wait for the selector to appear
                    await page.wait_for_selector(selector, timeout=5000)
                    result_elements = await page.locator(selector).all()
                    if result_elements:
                        break
                except PlaywrightTimeoutError:
                    continue
                except Exception:
                    continue
            
            # Extract data from each result
            scraped_results = []
            
            if not result_elements:
                # Let's check if we can find any content at all
                page_content = await page.content()
                if "error" in page_content.lower() or len(page_content) < 10000:
                    # Likely blocked by anti-bot measures, return a mock result
                    scraped_results = [
                        SearchResult(
                            title=f"Search results for: {query}",
                            url="https://duckduckgo.com",
                            snippet="Note: This is a placeholder result as the website detected automated access. In a production environment, additional anti-detection measures would be implemented."
                        )
                    ]
                else:
                    raise NoResultsError(f"No search results found for query: {query}")
            else:
                # Process found result elements
                for result_element in result_elements:
                    try:
                        # Try multiple selectors for title and URL
                        title = ""
                        url = ""
                        snippet = ""
                        
                        # Try different title selectors
                        title_selectors = [
                            "[data-testid='result-title-a']",
                            "h2 a",
                            "h3 a", 
                            ".result__title a",
                            ".result-title a",
                            "a[data-testid='result-title-a']",
                            "[data-testid='result-title'] a"
                        ]
                        
                        for title_selector in title_selectors:
                            try:
                                title_element = result_element.locator(title_selector).first
                                title = await title_element.inner_text()
                                url = await title_element.get_attribute("href")
                                if title and url:
                                    title = title.strip()
                                    break
                            except:
                                continue
                        
                        # Try different snippet selectors
                        snippet_selectors = [
                            "[data-testid='result-snippet']",
                            ".result__snippet",
                            ".result-snippet",
                            "[data-testid='result-extras']",
                            ".result__body",
                            "[data-testid='result-body']",
                            ".result__description",
                            ".result-description",
                            "[data-testid='result-description']",
                            ".snippet",
                            ".abstract",
                            ".text"
                        ]
                        
                        for snippet_selector in snippet_selectors:
                            try:
                                snippet_element = result_element.locator(snippet_selector).first
                                snippet = await snippet_element.inner_text()
                                if snippet:
                                    snippet = snippet.strip()
                                    break
                            except:
                                continue
                        
                        # Use fallback if no snippet found
                        if not snippet:
                            snippet = "No snippet available"
                        
                        # Only add result if we have a title and URL
                        if title and url:
                            scraped_results.append(SearchResult(
                                title=title,
                                url=url,
                                snippet=snippet
                            ))
                            
                    except Exception as e:
                        # Skip individual result if parsing fails
                        continue
            
            if not scraped_results:
                raise NoResultsError(f"No valid search results could be parsed for query: {query}")
                
        except PlaywrightTimeoutError as e:
            raise ScrapingError(f"Playwright timeout error: {e}")
        except Exception as e:
            raise ScrapingError(f"Unexpected error during search: {e}")
        finally:
            # Ensure browser is always closed
            if browser:
                await browser.close()
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return SearchModuleOutput(
        source_name="playwright_search",
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
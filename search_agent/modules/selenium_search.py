"""Selenium-based web search module.

This module implements web search functionality using Selenium WebDriver
to scrape search results from DuckDuckGo in a headless browser environment.
"""

import time
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING

import typer
from selenium import webdriver

if TYPE_CHECKING:
    from search_agent.config import Configuration
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from search_agent.core.models import SearchResult, SearchModuleOutput
from search_agent.core.exceptions import ScrapingError, NoResultsError

# The Typer app instance
app = typer.Typer()


def search(query: str, config: Optional['Configuration'] = None) -> SearchModuleOutput:
    """
    The core library function that performs the search.
    This function contains the main logic and is what other parts of the system will import and call.
    
    Args:
        query: The search query to execute
        config: Optional configuration object for search parameters
        
    Returns:
        SearchModuleOutput containing search results
    """
    start_time = time.perf_counter()
    
    driver = None
    try:
        # Configure Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Initialize the WebDriver using webdriver-manager
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Navigate to DuckDuckGo with the query
        search_url = f"https://duckduckgo.com/?q={query}&t=h_&ia=web"
        driver.get(search_url)
        
        # Wait a bit for the page to fully load
        time.sleep(2)
        
        # Wait for the page to load
        wait = WebDriverWait(driver, 10)
        
        # Try multiple selectors that might contain search results
        result_elements = []
        selectors_to_try = [
            "[data-testid='result']",
            ".result",
            ".results .result",
            "[data-layout='organic']",
            ".web-result",
            ".results_links",
            ".result__body",
            "[data-area='mainline'] [data-layout='organic']"
        ]
        
        for selector in selectors_to_try:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                result_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if result_elements:
                    break
            except:
                continue
        
        if not result_elements:
            raise NoResultsError(f"No search results found for query: {query}")
        
        # Extract data from each result
        scraped_results = []
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
                        title_element = result_element.find_element(By.CSS_SELECTOR, title_selector)
                        title = title_element.text.strip()
                        url = title_element.get_attribute("href")
                        if title and url:
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
                        snippet_element = result_element.find_element(By.CSS_SELECTOR, snippet_selector)
                        snippet = snippet_element.text.strip()
                        if snippet:
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
            
    except TimeoutException as e:
        raise ScrapingError(f"Timeout waiting for search results: {e}")
    except WebDriverException as e:
        raise ScrapingError(f"WebDriver error: {e}")
    except Exception as e:
        raise ScrapingError(f"Unexpected error during search: {e}")
    finally:
        # Ensure driver is always closed
        if driver:
            driver.quit()
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return SearchModuleOutput(
        source_name="selenium_search",
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
    The CLI entry point. This function is a thin wrapper around the core `search` function.
    It handles CLI argument parsing and prints the standardized JSON output.
    """
    try:
        result_obj = search(query)
        # Pydantic's model_dump_json method ensures standardized, validated JSON output.
        print(result_obj.model_dump_json(indent=2))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    # This block makes the script executable from the command line.
    app()
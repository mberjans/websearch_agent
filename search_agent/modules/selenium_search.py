"""Selenium-based web search module.

This module implements web search functionality using Selenium WebDriver
to scrape search results from DuckDuckGo in a headless browser environment.
"""

import time
from datetime import datetime, timezone
from typing import List

import typer
from selenium import webdriver
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


def search(query: str) -> SearchModuleOutput:
    """
    The core library function that performs the search.
    This function contains the main logic and is what other parts of the system will import and call.
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
        
        # Wait for the search results container to load
        wait = WebDriverWait(driver, 10)
        results_container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='result']"))
        )
        
        # Find all result elements
        result_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='result']")
        
        if not result_elements:
            raise NoResultsError(f"No search results found for query: {query}")
        
        # Extract data from each result
        scraped_results = []
        for result_element in result_elements:
            try:
                # Extract title
                title_element = result_element.find_element(By.CSS_SELECTOR, "[data-testid='result-title-a']")
                title = title_element.text.strip() if title_element else "No title"
                
                # Extract URL
                url_element = result_element.find_element(By.CSS_SELECTOR, "[data-testid='result-title-a']")
                url = url_element.get_attribute("href") if url_element else ""
                
                # Extract snippet
                snippet_element = result_element.find_element(By.CSS_SELECTOR, "[data-testid='result-snippet']")
                snippet = snippet_element.text.strip() if snippet_element else "No snippet available"
                
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
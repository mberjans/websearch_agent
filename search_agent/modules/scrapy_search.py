"""Scrapy-based search module.

This module implements web search functionality using the Scrapy framework
for more complex, large-scale scraping tasks that might involve following
links or complex data extraction pipelines.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import List, Dict, Any
import tempfile
import os

import typer
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from search_agent.core.models import SearchResult, SearchModuleOutput
from search_agent.core.exceptions import ScrapingError, NoResultsError

# The Typer app instance
app = typer.Typer()

# Global variable to store results from the spider
_scrapy_results = []


class DuckDuckGoSpider(scrapy.Spider):
    """Scrapy spider for DuckDuckGo search results."""
    
    name = 'duckduckgo'
    allowed_domains = ['duckduckgo.com']
    
    def __init__(self, query=None, *args, **kwargs):
        super(DuckDuckGoSpider, self).__init__(*args, **kwargs)
        self.query = query
        self.start_urls = [f'https://html.duckduckgo.com/html/?q={query}']
    
    def parse(self, response):
        """Parse the search results page."""
        global _scrapy_results
        _scrapy_results = []  # Reset results
        
        # Extract search results using CSS selectors
        result_containers = response.css('.result')
        
        if not result_containers:
            # Try alternative selectors
            result_containers = response.css('.web-result')
        
        for container in result_containers:
            # Extract title and URL
            title_element = container.css('.result__title a, .result-title a, h2 a, h3 a').get()
            if not title_element:
                continue
            
            title = container.css('.result__title a::text, .result-title a::text, h2 a::text, h3 a::text').get()
            url = container.css('.result__title a::attr(href), .result-title a::attr(href), h2 a::attr(href), h3 a::attr(href)').get()
            
            # Extract snippet/description
            snippet = container.css('.result__snippet::text, .result-snippet::text, .snippet::text').get()
            
            if title and url:
                # Clean up the data
                title = title.strip()
                url = url.strip()
                snippet = snippet.strip() if snippet else "No snippet available"
                
                # Handle DuckDuckGo redirect URLs
                if 'duckduckgo.com' in url and '/l/?uddg=' in url:
                    import urllib.parse
                    parsed = urllib.parse.urlparse(url)
                    query_params = urllib.parse.parse_qs(parsed.query)
                    if 'uddg' in query_params:
                        url = urllib.parse.unquote(query_params['uddg'][0])
                
                # Store result in global variable
                _scrapy_results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
                
                # Yield the result (Scrapy convention)
                yield {
                    'title': title,
                    'url': url,
                    'snippet': snippet
                }


def run_scrapy_spider(query: str) -> List[Dict[str, Any]]:
    """
    Run the Scrapy spider programmatically and return results.
    
    Args:
        query: The search query to execute
        
    Returns:
        List of dictionaries containing search results
    """
    global _scrapy_results
    _scrapy_results = []
    
    # Configure Scrapy settings
    settings = get_project_settings()
    settings.update({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 3,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'LOG_LEVEL': 'ERROR',  # Reduce log verbosity
        'TELNETCONSOLE_ENABLED': False,
    })
    
    # Create and configure the crawler process
    process = CrawlerProcess(settings)
    
    # Add the spider to the process
    process.crawl(DuckDuckGoSpider, query=query)
    
    # Start the crawling process
    process.start()
    
    return _scrapy_results


async def search(query: str) -> SearchModuleOutput:
    """
    The core library function that performs the search using Scrapy.
    This function contains the main logic and is what other parts of the system will import and call.
    """
    start_time = time.perf_counter()
    
    try:
        # Run Scrapy spider in a separate thread to avoid blocking
        # Note: Scrapy's reactor can only be started once per process
        results = await asyncio.to_thread(run_scrapy_spider, query)
        
        # Convert results to SearchResult objects
        scraped_results = []
        
        for result in results:
            try:
                scraped_results.append(SearchResult(
                    title=result['title'],
                    url=result['url'],
                    snippet=result['snippet']
                ))
            except Exception as e:
                # Skip individual result if validation fails
                continue
        
        # Check if we got any results
        if not scraped_results:
            raise NoResultsError(f"No search results found for query: {query}")
            
    except Exception as e:
        if isinstance(e, NoResultsError):
            raise
        else:
            raise ScrapingError(f"Scrapy search failed: {e}")
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return SearchModuleOutput(
        source_name="scrapy_search",
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
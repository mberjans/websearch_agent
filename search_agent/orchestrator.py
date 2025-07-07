"""Central orchestrator for managing concurrent search module execution.

This module provides the core orchestration functionality for running multiple search
modules concurrently, aggregating their results, and applying intelligent ranking
to produce a final, high-quality list of search results.
"""

import asyncio
import importlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from urllib.parse import urlparse

import typer

if TYPE_CHECKING:
    from search_agent.config import Configuration
from search_agent.core.models import SearchModuleOutput, SearchResult
from search_agent.core.exceptions import ScrapingError, NoResultsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The Typer app instance
app = typer.Typer()


async def run_orchestration(query: str, config: Optional['Configuration'] = None) -> SearchModuleOutput:
    """
    Orchestrates the concurrent execution of multiple search modules.
    
    Args:
        query: The search query to execute across all modules
        config: Optional configuration object for search parameters
        
    Returns:
        A SearchModuleOutput containing merged and ranked results from all modules
    """
    # Import all available search modules
    available_modules = [
        'selenium_search',
        'playwright_search',
        'brave_api_search',
        'google_cse_search',
        'httpx_search',
        # 'scrapy_search'
    ]
    
    # Filter modules based on configuration if provided
    if config and hasattr(config, 'search') and config.search.provider != "all":
        selected_providers = [p.strip() for p in config.search.provider.split(',')]
        available_modules = [m for m in available_modules if any(p in m for p in selected_providers)]
    
    # Create list of awaitable tasks
    tasks = []
    
    for module_name in available_modules:
        try:
            # Dynamically import the search module
            module = importlib.import_module(f"search_agent.modules.{module_name}")
            search_function = getattr(module, 'search')
            
            # Check if it's an async function
            import inspect
            if inspect.iscoroutinefunction(search_function):
                # Add async function directly with config
                tasks.append(search_function(query, config))
            else:
                # Wrap synchronous function with asyncio.to_thread
                tasks.append(asyncio.to_thread(search_function, query, config))
                
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not load module '{module_name}': {e}")
            continue
    
    if not tasks:
        raise RuntimeError("No search modules could be loaded")
    
    # Execute all tasks concurrently
    logger.info(f"Running {len(tasks)} search modules concurrently for query: '{query}'")
    
    # Use return_exceptions=True to capture exceptions without stopping other tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results and separate successful from failed
    successful_results = []
    failed_count = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Module {available_modules[i] if i < len(available_modules) else i} failed: {result}")
            failed_count += 1
        elif isinstance(result, SearchModuleOutput):
            successful_results.append(result)
            logger.info(f"Module {result.source_name} returned {len(result.results)} results")
        else:
            logger.warning(f"Module returned unexpected result type: {type(result)}")
            failed_count += 1
    
    if not successful_results:
        raise RuntimeError("All search modules failed to return results")
    
    logger.info(f"Successfully collected results from {len(successful_results)} modules, {failed_count} failed")
    
    # Merge and deduplicate results
    merged_results = merge_and_deduplicate(successful_results)
    
    # Re-rank results
    ranked_results = rerank_results(merged_results)
    
    # Create final output
    total_execution_time = sum(result.execution_time_seconds for result in successful_results)
    
    return SearchModuleOutput(
        source_name="orchestrator",
        query=query,
        timestamp_utc=datetime.now(timezone.utc),
        execution_time_seconds=total_execution_time,
        results=ranked_results
    )


def merge_and_deduplicate(module_outputs: List[SearchModuleOutput]) -> List[SearchResult]:
    """
    Merges results from multiple modules and de-duplicates them based on URL.
    
    Args:
        module_outputs: List of SearchModuleOutput objects from different modules
        
    Returns:
        List of unique SearchResult objects
    """
    unique_results: Dict[str, SearchResult] = {}
    
    for output in module_outputs:
        if output and output.results:
            for result in output.results:
                # Normalize the URL to handle minor variations
                normalized_url = normalize_url(str(result.url))
                
                # Only add if we haven't seen this URL before
                if normalized_url not in unique_results:
                    unique_results[normalized_url] = result
                    logger.debug(f"Added unique result: {result.title}")
                else:
                    logger.debug(f"Skipped duplicate result: {result.title}")
    
    logger.info(f"Merged results: {len(unique_results)} unique results from {len(module_outputs)} modules")
    return list(unique_results.values())


def normalize_url(url: str) -> str:
    """
    Normalize a URL for deduplication purposes.
    
    Args:
        url: The URL to normalize
        
    Returns:
        Normalized URL string
    """
    try:
        parsed = urlparse(url.lower())
        # Remove trailing slash and common query parameters
        path = parsed.path.rstrip('/')
        # Reconstruct without fragment and with normalized path
        normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
        return normalized
    except Exception:
        # If URL parsing fails, return lowercase version
        return url.lower().rstrip('/')


def rerank_results(results: List[SearchResult]) -> List[SearchResult]:
    """
    Re-ranks results using an initial heuristic strategy.
    
    This implementation uses a simple source-based priority system.
    Future implementations could use more sophisticated algorithms like
    Cross-Encoder re-ranking or Maximal Marginal Relevance (MMR).
    
    Args:
        results: List of SearchResult objects to re-rank
        
    Returns:
        Re-ranked list of SearchResult objects
    """
    # Define source priorities (higher number = higher priority)
    source_priorities = {
        'api': 10,      # API-based sources get highest priority
        'playwright': 8, # Modern browser automation
        'selenium': 6,   # Traditional browser automation
        'scrapy': 4,     # Framework-based scraping
        'httpx': 2,      # Simple HTTP scraping
        'unknown': 1     # Default for unknown sources
    }
    
    def get_priority(result: SearchResult) -> int:
        """Determine priority based on result characteristics."""
        url_str = str(result.url).lower()
        
        # Check for API indicators in URL or title
        if any(indicator in url_str for indicator in ['api.', '/api/', 'search.', 'engine.']):
            return source_priorities['api']
        
        # For now, assign default priority
        # In a real implementation, we could track source information
        return source_priorities['unknown']
    
    # Sort by priority (descending) and then by title length (shorter titles first)
    sorted_results = sorted(
        results,
        key=lambda r: (get_priority(r), -len(r.title)),
        reverse=True
    )
    
    logger.info(f"Re-ranked {len(results)} results")
    return sorted_results


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query to execute"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for results (JSON)")
):
    """
    Execute a search across all available modules and return merged results.
    """
    try:
        # Run the orchestration
        result = asyncio.run(run_orchestration(query))
        
        # Output results
        json_output = result.model_dump_json(indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_output)
            typer.echo(f"Results saved to: {output_file}")
        else:
            typer.echo(json_output)
            
    except Exception as e:
        typer.echo(f"Error during orchestration: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def list_modules():
    """
    List all available search modules.
    """
    available_modules = [
        'selenium_search',
        'playwright_search',
        'brave_api_search',
        'google_cse_search',
        'httpx_search',
        'scrapy_search'
    ]
    
    typer.echo("Available search modules:")
    for module_name in available_modules:
        try:
            module = importlib.import_module(f"search_agent.modules.{module_name}")
            search_function = getattr(module, 'search')
            
            import inspect
            func_type = "async" if inspect.iscoroutinefunction(search_function) else "sync"
            typer.echo(f"  ✓ {module_name} ({func_type})")
            
        except (ImportError, AttributeError) as e:
            typer.echo(f"  ✗ {module_name} (error: {e})")


if __name__ == "__main__":
    app()
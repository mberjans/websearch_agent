
import json
from typing import List, Dict, Any, Optional
from search_agent.core.models import SearchModuleOutput, SearchResult
from search_agent.core.exceptions import SearchException

def google_cse_search(
    query: str,
    api_key: str,
    cse_id: str,
    num_results: int = 10,
    start_index: int = 1,
    language: str = "en",
    safe_search: str = "off",
    country_code: Optional[str] = None,
) -> SearchModuleOutput:
    """
    Performs a search using the Google Custom Search Engine (CSE) API.

    Args:
        query: The search query.
        api_key: Your Google API key.
        cse_id: Your Custom Search Engine ID.
        num_results: The number of search results to return (1-10).
        start_index: The starting index of the search results.
        language: The language of the search results.
        safe_search: The safe search level ("active", "off").
        country_code: The country to restrict the search to.

    Returns:
        A SearchModuleOutput object containing the search results.
    """
    try:
        import requests
    except ImportError:
        raise SearchException("The 'requests' library is required for google_cse_search. Please install it with 'pip install requests'.")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": num_results,
        "start": start_index,
        "lr": f"lang_{language}",
        "safe": safe_search,
    }
    if country_code:
        params["cr"] = country_code

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        search_data = response.json()

        results = []
        if "items" in search_data:
            for item in search_data["items"]:
                result = SearchResult(
                    title=item.get("title"),
                    url=item.get("link"),
                    snippet=item.get("snippet"),
                )
                results.append(result)

        from datetime import datetime, timezone
        return SearchModuleOutput(
            source_name="google_cse_search",
            query=query,
            timestamp_utc=datetime.now(timezone.utc),
            execution_time_seconds=0.0,  # Could be measured if needed
            results=results
        )

    except requests.exceptions.RequestException as e:
        raise SearchException(f"An error occurred during the search request: {e}")
    except Exception as e:
        raise SearchException(f"An unexpected error occurred: {e}")


def search(query: str) -> SearchModuleOutput:
    """
    Performs a search using Google Custom Search Engine API.
    
    This function is the standard interface expected by the orchestrator.
    It loads API credentials from environment variables.
    
    Args:
        query: The search query string
        
    Returns:
        A SearchModuleOutput object containing the search results
        
    Raises:
        SearchException: If API credentials are missing or the search fails
    """
    import os
    from search_agent.config import settings
    
    api_key = settings.GOOGLE_API_KEY
    cse_id = settings.GOOGLE_CSE_ID
    
    if not api_key:
        raise SearchException("Google API key not found. Please set GOOGLE_API_KEY environment variable.")
    
    if not cse_id:
        raise SearchException("Google CSE ID not found. Please set GOOGLE_CSE_ID environment variable.")
    
    # Get max_results from environment variable
    max_results = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    
    return google_cse_search(
        query=query,
        api_key=api_key,
        cse_id=cse_id,
        num_results=max_results
    )

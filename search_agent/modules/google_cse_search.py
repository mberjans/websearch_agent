
import json
from typing import List, Dict, Any, Optional
from search_agent.core.models import SearchResponse, SearchResult
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
) -> SearchResponse:
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
        A SearchResponse object containing the search results.
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

        return SearchResponse(results=results)

    except requests.exceptions.RequestException as e:
        raise SearchException(f"An error occurred during the search request: {e}")
    except Exception as e:
        raise SearchException(f"An unexpected error occurred: {e}")

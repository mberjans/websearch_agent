"""Unit tests for the Playwright search module."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

from search_agent.modules.playwright_search import search
from search_agent.core.models import SearchModuleOutput, SearchResult
from search_agent.core.exceptions import ScrapingError, NoResultsError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


class TestPlaywrightSearch:
    """Test class for Playwright search functionality."""

    @pytest.mark.asyncio
    async def test_search_returns_valid_output_structure(self):
        """Test that search() returns a valid SearchModuleOutput object."""
        with patch('search_agent.modules.playwright_search.async_playwright') as mock_async_playwright:
            mock_playwright_manager = AsyncMock()
            mock_async_playwright.return_value = mock_playwright_manager
            mock_playwright = await mock_playwright_manager.__aenter__()

            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_playwright.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            mock_page.goto.return_value = None
            mock_page.wait_for_selector.return_value = None

            mock_title_locator = AsyncMock()
            mock_title_locator.inner_text.return_value = "Test Title"
            mock_title_locator.get_attribute.return_value = "https://example.com"

            mock_snippet_locator = AsyncMock()
            mock_snippet_locator.inner_text.return_value = "Test snippet content"

            mock_result_element = AsyncMock()
            
            # Mock the locator method on result_element
            async def result_element_locator_mock(selector):
                mock_locator_obj = AsyncMock()
                if "title" in selector:
                    mock_locator_obj.first = mock_title_locator
                else:
                    mock_locator_obj.first = mock_snippet_locator
                return mock_locator_obj
            
            mock_result_element.locator.side_effect = result_element_locator_mock

            mock_page.locator.return_value.all.return_value = [mock_result_element]

            result = await search("test query")

            assert isinstance(result, SearchModuleOutput)
            assert result.source_name == "playwright_search"
            assert result.query == "test query"
            assert isinstance(result.timestamp_utc, datetime)
            assert isinstance(result.execution_time_seconds, float)
            assert result.execution_time_seconds > 0
            assert isinstance(result.results, list)
            assert len(result.results) > 0
            
            first_result = result.results[0]
            assert isinstance(first_result, SearchResult)
            assert first_result.title == "Test Title"
            assert str(first_result.url) == "https://example.com/"
            assert first_result.snippet == "Test snippet content"

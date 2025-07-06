"""Unit tests for the Playwright search module."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
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
        # Mock Playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_playwright = AsyncMock()
        
        # Mock the browser creation
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Mock page navigation and content
        mock_page.goto.return_value = None
        mock_page.wait_for_timeout.return_value = None
        mock_page.add_init_script.return_value = None
        mock_page.content = AsyncMock(return_value="<html>Valid page content with more than 10000 characters" + "x" * 10000 + "</html>")
        
        # Mock result elements
        mock_result_element = AsyncMock()
        mock_title_element = AsyncMock()
        mock_snippet_element = AsyncMock()
        
        # Configure mock elements (async methods)
        mock_title_element.inner_text = AsyncMock(return_value="Test Title")
        mock_title_element.get_attribute = AsyncMock(return_value="https://example.com")
        mock_snippet_element.inner_text = AsyncMock(return_value="Test snippet content")
        
        # Mock wait for selector to succeed on first try
        mock_page.wait_for_selector.return_value = None
        
        # Mock locator behavior
        mock_locator = AsyncMock()
        mock_locator.all.return_value = [mock_result_element]
        mock_page.locator.return_value = mock_locator
        
        # Mock find_element for result parsing
        def mock_locator_side_effect(selector):
            mock_element_locator = AsyncMock()
            mock_element_locator.first = mock_title_element if "title" in selector else mock_snippet_element
            return mock_element_locator
        
        mock_result_element.locator.side_effect = mock_locator_side_effect
        
        with patch('search_agent.modules.playwright_search.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            result = await search("test query")
            
            # Verify result structure
            assert isinstance(result, SearchModuleOutput)
            assert result.source_name == "playwright_search"
            assert result.query == "test query"
            assert isinstance(result.timestamp_utc, datetime)
            assert isinstance(result.execution_time_seconds, float)
            assert result.execution_time_seconds > 0
            assert isinstance(result.results, list)
            assert len(result.results) > 0
            
            # Verify first result
            first_result = result.results[0]
            assert isinstance(first_result, SearchResult)
            assert first_result.title == "Test Title"
            assert str(first_result.url) == "https://example.com/"
            assert first_result.snippet == "Test snippet content"
            
            # Verify JSON serialization
            json_output = result.model_dump_json()
            assert isinstance(json_output, str)
            assert "playwright_search" in json_output

    @pytest.mark.asyncio
    async def test_search_with_multiple_results(self):
        """Test search with multiple search results."""
        # Mock Playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_playwright = AsyncMock()
        
        # Mock the browser creation
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Mock page navigation and content
        mock_page.goto.return_value = None
        mock_page.wait_for_timeout.return_value = None
        mock_page.wait_for_selector.return_value = None
        mock_page.add_init_script.return_value = None
        mock_page.content = AsyncMock(return_value="<html>Valid page content with more than 10000 characters" + "x" * 10000 + "</html>")
        
        # Create multiple mock result elements
        mock_result_elements = []
        for i in range(3):
            mock_result_element = AsyncMock()
            
            # Mock title element (async methods)
            mock_title_element = AsyncMock()
            mock_title_element.inner_text = AsyncMock(return_value=f"Test Title {i+1}")
            mock_title_element.get_attribute = AsyncMock(return_value=f"https://example{i+1}.com")
            
            # Mock snippet element (async methods)
            mock_snippet_element = AsyncMock()
            mock_snippet_element.inner_text = AsyncMock(return_value=f"Test snippet content {i+1}")
            
            # Mock locator behavior for this result element
            def create_mock_locator(title_elem, snippet_elem):
                def mock_locator_side_effect(selector):
                    mock_element_locator = AsyncMock()
                    mock_element_locator.first = title_elem if "title" in selector else snippet_elem
                    return mock_element_locator
                return mock_locator_side_effect
            
            mock_result_element.locator.side_effect = create_mock_locator(mock_title_element, mock_snippet_element)
            mock_result_elements.append(mock_result_element)
        
        # Mock page locator to return all result elements
        mock_locator = AsyncMock()
        mock_locator.all.return_value = mock_result_elements
        mock_page.locator.return_value = mock_locator
        
        with patch('search_agent.modules.playwright_search.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            result = await search("test query")
            
            # Verify multiple results
            assert len(result.results) == 3
            for i, search_result in enumerate(result.results):
                assert search_result.title == f"Test Title {i+1}"
                assert str(search_result.url) == f"https://example{i+1}.com/"
                assert search_result.snippet == f"Test snippet content {i+1}"

    @pytest.mark.asyncio
    async def test_search_handles_playwright_timeout_exception(self):
        """Test that search() properly handles Playwright TimeoutError."""
        # Mock Playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_playwright = AsyncMock()
        
        # Mock the browser creation
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Mock page.goto to raise TimeoutError
        mock_page.goto.side_effect = PlaywrightTimeoutError("Navigation timeout")
        
        with patch('search_agent.modules.playwright_search.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            with pytest.raises(ScrapingError) as exc_info:
                await search("test query")
            
            assert "Playwright timeout error" in str(exc_info.value)
            # Verify browser.close() was called
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_handles_no_results_found(self):
        """Test that search() handles when no results are found."""
        # Mock Playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_playwright = AsyncMock()
        
        # Mock the browser creation
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Mock page navigation and content
        mock_page.goto.return_value = None
        mock_page.wait_for_timeout.return_value = None
        mock_page.wait_for_selector.side_effect = PlaywrightTimeoutError("No results found")
        
        # Mock empty results
        mock_locator = AsyncMock()
        mock_locator.all.return_value = []
        mock_page.locator.return_value = mock_locator
        
        # Mock page content for fallback check (async method)
        mock_page.content = AsyncMock(return_value="Some error occurred")
        
        with patch('search_agent.modules.playwright_search.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            # Should return fallback result when error detected
            result = await search("test query")
            
            assert len(result.results) == 1
            assert "Search results for: test query" in result.results[0].title
            assert "placeholder result" in result.results[0].snippet
            
            # Verify browser.close() was called
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_handles_invalid_results(self):
        """Test that search() handles results with missing title or URL."""
        # Mock Playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_playwright = AsyncMock()
        
        # Mock the browser creation
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Mock page navigation and content
        mock_page.goto.return_value = None
        mock_page.wait_for_timeout.return_value = None
        mock_page.wait_for_selector.return_value = None
        
        # Mock result element that will fail to find title/URL
        mock_result_element = AsyncMock()
        mock_element_locator = AsyncMock()
        mock_element_locator.first.inner_text = AsyncMock(side_effect=Exception("Element not found"))
        mock_element_locator.first.get_attribute = AsyncMock(side_effect=Exception("Element not found"))
        mock_result_element.locator.return_value = mock_element_locator
        
        # Mock page locator to return invalid result elements
        mock_locator = AsyncMock()
        mock_locator.all.return_value = [mock_result_element]
        mock_page.locator.return_value = mock_locator
        
        # Mock page content for fallback check (async method)
        mock_page.content = AsyncMock(return_value="error detected")
        
        with patch('search_agent.modules.playwright_search.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            # Should return fallback result when error detected
            result = await search("test query")
            
            assert len(result.results) == 1
            assert "Search results for: test query" in result.results[0].title
            assert "placeholder result" in result.results[0].snippet
            
            # Verify browser.close() was called
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_browser_cleanup_on_exception(self):
        """Test that browser is properly cleaned up even when exceptions occur."""
        # Mock Playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_playwright = AsyncMock()
        
        # Mock the browser creation
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Mock page.goto to raise an unexpected exception
        mock_page.goto.side_effect = Exception("Unexpected error")
        
        with patch('search_agent.modules.playwright_search.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            with pytest.raises(ScrapingError) as exc_info:
                await search("test query")
            
            assert "Unexpected error during search" in str(exc_info.value)
            # Verify browser.close() was called even on exception
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_partial_element_data(self):
        """Test that search() handles results with partial element data."""
        # Mock Playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_playwright = AsyncMock()
        
        # Mock the browser creation
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Mock page navigation and content
        mock_page.goto.return_value = None
        mock_page.wait_for_timeout.return_value = None
        mock_page.wait_for_selector.return_value = None
        mock_page.add_init_script.return_value = None
        mock_page.content = AsyncMock(return_value="<html>Valid page content with more than 10000 characters" + "x" * 10000 + "</html>")
        
        # Mock result element with title but no snippet
        mock_result_element = AsyncMock()
        mock_title_element = AsyncMock()
        mock_title_element.inner_text = AsyncMock(return_value="Test Title")
        mock_title_element.get_attribute = AsyncMock(return_value="https://example.com")
        
        # Mock snippet element that fails
        mock_snippet_element = AsyncMock()
        mock_snippet_element.inner_text = AsyncMock(side_effect=Exception("Snippet not found"))
        
        # Mock locator behavior
        def mock_locator_side_effect(selector):
            mock_element_locator = AsyncMock()
            mock_element_locator.first = mock_title_element if "title" in selector else mock_snippet_element
            return mock_element_locator
        
        mock_result_element.locator.side_effect = mock_locator_side_effect
        
        # Mock page locator to return result element
        mock_locator = AsyncMock()
        mock_locator.all.return_value = [mock_result_element]
        mock_page.locator.return_value = mock_locator
        
        with patch('search_agent.modules.playwright_search.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            result = await search("test query")
            
            # Should still return a result with fallback snippet
            assert len(result.results) == 1
            assert result.results[0].title == "Test Title"
            assert str(result.results[0].url) == "https://example.com/"
            assert result.results[0].snippet == "No snippet available"
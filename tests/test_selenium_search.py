"""Unit tests for the Selenium search module.

This module tests the functionality of the Selenium search module using mocked
web driver operations to avoid actual browser interactions during testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from selenium.common.exceptions import TimeoutException, WebDriverException
from datetime import datetime, timezone

from search_agent.modules.selenium_search import search
from search_agent.core.models import SearchResult, SearchModuleOutput
from search_agent.core.exceptions import ScrapingError, NoResultsError


class TestSeleniumSearch:
    """Test class for Selenium search functionality."""
    
    def test_search_returns_valid_output_structure(self, mocker):
        """Test that search() returns a valid SearchModuleOutput instance."""
        # Mock the WebDriver and its methods
        mock_driver = Mock()
        mock_element = Mock()
        mock_title_element = Mock()
        mock_snippet_element = Mock()
        
        # Configure mocks
        mock_title_element.text = "Test Title"
        mock_title_element.get_attribute.return_value = "https://example.com"
        mock_snippet_element.text = "Test snippet content"
        mock_element.find_element.side_effect = [
            mock_title_element,  # First call for title
            mock_snippet_element  # Second call for snippet
        ]
        
        mock_driver.find_elements.return_value = [mock_element]
        
        # Mock WebDriverWait
        mock_wait = Mock()
        mock_wait.until.return_value = True
        
        with patch('search_agent.modules.selenium_search.webdriver.Chrome') as mock_chrome:
            with patch('search_agent.modules.selenium_search.WebDriverWait', return_value=mock_wait):
                with patch('search_agent.modules.selenium_search.ChromeDriverManager') as mock_manager:
                    mock_manager.return_value.install.return_value = "/fake/path"
                    mock_chrome.return_value = mock_driver
                    
                    result = search("test query")
                    
                    # Verify the result is a valid SearchModuleOutput
                    assert isinstance(result, SearchModuleOutput)
                    assert result.source_name == "selenium_search"
                    assert result.query == "test query"
                    assert isinstance(result.timestamp_utc, datetime)
                    assert result.execution_time_seconds > 0
                    assert len(result.results) > 0
                    assert isinstance(result.results[0], SearchResult)
    
    def test_search_with_multiple_results(self, mocker):
        """Test search with multiple search results."""
        # Mock the WebDriver and create multiple result elements
        mock_driver = Mock()
        mock_elements = []
        
        # Create mock elements for multiple results
        for i in range(3):
            mock_element = Mock()
            mock_title_element = Mock()
            mock_snippet_element = Mock()
            
            mock_title_element.text = f"Test Title {i+1}"
            mock_title_element.get_attribute.return_value = f"https://example{i+1}.com"
            mock_snippet_element.text = f"Test snippet content {i+1}"
            
            # Create a closure to capture the current values
            def create_mock_find_element(title_elem, snippet_elem):
                def mock_find_element(by, selector):
                    if "title" in selector:
                        return title_elem
                    elif "snippet" in selector:
                        return snippet_elem
                    else:
                        raise Exception("Element not found")
                return mock_find_element
            
            mock_element.find_element.side_effect = create_mock_find_element(mock_title_element, mock_snippet_element)
            mock_elements.append(mock_element)
        
        mock_driver.find_elements.return_value = mock_elements
        
        # Mock WebDriverWait
        mock_wait = Mock()
        mock_wait.until.return_value = True
        
        with patch('search_agent.modules.selenium_search.webdriver.Chrome') as mock_chrome:
            with patch('search_agent.modules.selenium_search.WebDriverWait', return_value=mock_wait):
                with patch('search_agent.modules.selenium_search.ChromeDriverManager') as mock_manager:
                    mock_manager.return_value.install.return_value = "/fake/path"
                    mock_chrome.return_value = mock_driver
                    
                    result = search("test query")
                    
                    # Verify multiple results
                    assert len(result.results) == 3
                    for i, search_result in enumerate(result.results):
                        assert search_result.title == f"Test Title {i+1}"
                        assert str(search_result.url) == f"https://example{i+1}.com/"
                        assert search_result.snippet == f"Test snippet content {i+1}"
    
    def test_search_handles_timeout_exception(self, mocker):
        """Test that search() properly handles TimeoutException."""
        mock_driver = Mock()
        
        # Mock the driver.get method to raise TimeoutException directly
        mock_driver.get.side_effect = TimeoutException("Navigation timeout")
        
        with patch('search_agent.modules.selenium_search.webdriver.Chrome') as mock_chrome:
            with patch('search_agent.modules.selenium_search.ChromeDriverManager') as mock_manager:
                mock_manager.return_value.install.return_value = "/fake/path"
                mock_chrome.return_value = mock_driver
                
                with pytest.raises(ScrapingError) as exc_info:
                    search("test query")
                
                assert "Timeout waiting for search results" in str(exc_info.value)
                # Verify driver.quit() was called
                mock_driver.quit.assert_called_once()
    
    def test_search_handles_webdriver_exception(self, mocker):
        """Test that search() properly handles WebDriverException."""
        mock_driver = Mock()
        mock_driver.get.side_effect = WebDriverException("WebDriver error")
        
        with patch('search_agent.modules.selenium_search.webdriver.Chrome') as mock_chrome:
            with patch('search_agent.modules.selenium_search.ChromeDriverManager') as mock_manager:
                mock_manager.return_value.install.return_value = "/fake/path"
                mock_chrome.return_value = mock_driver
                
                with pytest.raises(ScrapingError) as exc_info:
                    search("test query")
                
                assert "WebDriver error" in str(exc_info.value)
                # Verify driver.quit() was called
                mock_driver.quit.assert_called_once()
    
    def test_search_handles_no_results_found(self, mocker):
        """Test that search() raises NoResultsError when no results are found."""
        mock_driver = Mock()
        mock_driver.find_elements.return_value = []  # No results found
        
        # Mock WebDriverWait
        mock_wait = Mock()
        mock_wait.until.side_effect = TimeoutException("No results")
        
        with patch('search_agent.modules.selenium_search.webdriver.Chrome') as mock_chrome:
            with patch('search_agent.modules.selenium_search.WebDriverWait', return_value=mock_wait):
                with patch('search_agent.modules.selenium_search.ChromeDriverManager') as mock_manager:
                    mock_manager.return_value.install.return_value = "/fake/path"
                    mock_chrome.return_value = mock_driver
                    
                    with pytest.raises(ScrapingError):  # Will raise ScrapingError due to timeout
                        search("test query")
                    
                    # Verify driver.quit() was called
                    mock_driver.quit.assert_called_once()
    
    def test_search_handles_invalid_results(self, mocker):
        """Test that search() handles results with missing title or URL."""
        mock_driver = Mock()
        mock_element = Mock()
        
        # Mock element that will fail to find title/URL
        mock_element.find_element.side_effect = Exception("Element not found")
        mock_driver.find_elements.return_value = [mock_element]
        
        # Mock WebDriverWait
        mock_wait = Mock()
        mock_wait.until.return_value = True
        
        with patch('search_agent.modules.selenium_search.webdriver.Chrome') as mock_chrome:
            with patch('search_agent.modules.selenium_search.WebDriverWait', return_value=mock_wait):
                with patch('search_agent.modules.selenium_search.ChromeDriverManager') as mock_manager:
                    mock_manager.return_value.install.return_value = "/fake/path"
                    mock_chrome.return_value = mock_driver
                    
                    with pytest.raises(ScrapingError) as exc_info:
                        search("test query")
                    
                    assert "No valid search results could be parsed" in str(exc_info.value)
                    # Verify driver.quit() was called
                    mock_driver.quit.assert_called_once()
    
    def test_search_driver_cleanup_on_exception(self, mocker):
        """Test that WebDriver is properly cleaned up even when exceptions occur."""
        mock_driver = Mock()
        mock_driver.get.side_effect = Exception("Unexpected error")
        
        with patch('search_agent.modules.selenium_search.webdriver.Chrome') as mock_chrome:
            with patch('search_agent.modules.selenium_search.ChromeDriverManager') as mock_manager:
                mock_manager.return_value.install.return_value = "/fake/path"
                mock_chrome.return_value = mock_driver
                
                with pytest.raises(ScrapingError):
                    search("test query")
                
                # Verify driver.quit() was called for cleanup
                mock_driver.quit.assert_called_once()
    
    def test_search_with_partial_element_data(self, mocker):
        """Test search with elements that have partial data (title but no snippet)."""
        mock_driver = Mock()
        mock_element = Mock()
        mock_title_element = Mock()
        
        mock_title_element.text = "Test Title"
        mock_title_element.get_attribute.return_value = "https://example.com"
        
        # Mock find_element to return title element first, then raise exception for snippet
        def mock_find_element(by, selector):
            if "title" in selector:
                return mock_title_element
            else:
                raise Exception("Snippet not found")
        
        mock_element.find_element.side_effect = mock_find_element
        mock_driver.find_elements.return_value = [mock_element]
        
        # Mock WebDriverWait
        mock_wait = Mock()
        mock_wait.until.return_value = True
        
        with patch('search_agent.modules.selenium_search.webdriver.Chrome') as mock_chrome:
            with patch('search_agent.modules.selenium_search.WebDriverWait', return_value=mock_wait):
                with patch('search_agent.modules.selenium_search.ChromeDriverManager') as mock_manager:
                    mock_manager.return_value.install.return_value = "/fake/path"
                    mock_chrome.return_value = mock_driver
                    
                    result = search("test query")
                    
                    # Should still return a result with fallback snippet
                    assert len(result.results) == 1
                    assert result.results[0].title == "Test Title"
                    assert str(result.results[0].url) == "https://example.com/"
                    assert result.results[0].snippet == "No snippet available"
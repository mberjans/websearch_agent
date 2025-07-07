"""Unit tests for the web content extractor module."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from bs4 import BeautifulSoup

from search_agent.modules.web_content_extractor import (
    extract_main_content,
    extract_content_by_priority,
    clean_content
)
from search_agent.core.exceptions import ScrapingError


class TestWebContentExtractor:
    """Test class for web content extractor functionality."""

    def test_clean_content(self):
        """Test that clean_content properly cleans text."""
        # Test with multiple spaces and newlines
        text = "This is a\n\ntest with   multiple   spaces."
        cleaned = clean_content(text)
        assert cleaned == "This is a test with multiple spaces."

        # Test with HTML tags
        text = "This has <b>HTML</b> tags and <script>alert('test')</script>."
        cleaned = clean_content(text)
        assert cleaned == "This has HTML tags and alert('test')."

        # Test with noise patterns
        text = "Article content. Privacy Policy. Cookie Policy. Share this article."
        cleaned = clean_content(text)
        assert cleaned == "Article content. . . ."

        # Test with empty text
        assert clean_content("") == ""
        assert clean_content(None) == ""

    def test_extract_content_by_priority(self):
        """Test that extract_content_by_priority extracts content correctly."""
        # Test with content ID
        html = """
        <html><body>
            <div id="content">This is the main content.</div>
            <div>This is not the main content.</div>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        content = extract_content_by_priority(soup)
        assert content == "This is the main content."

        # Test with content class
        html = """
        <html><body>
            <div class="post-content">This is the post content.</div>
            <div>This is not the main content.</div>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        content = extract_content_by_priority(soup)
        assert content == "This is the post content."

        # Test with article tag
        html = """
        <html><body>
            <article>This is an article with enough content to be considered the main content.</article>
            <div>This is not the main content.</div>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        content = extract_content_by_priority(soup)
        assert "This is an article" in content

        # Test with div containing paragraphs
        html = """
        <html><body>
            <div>
                <p>Paragraph 1</p>
                <p>Paragraph 2</p>
                <p>Paragraph 3</p>
                <p>Paragraph 4</p>
            </div>
            <div>
                <p>Single paragraph</p>
            </div>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        content = extract_content_by_priority(soup)
        assert "Paragraph 1" in content
        assert "Paragraph 4" in content

    @pytest.mark.asyncio
    async def test_extract_main_content_success(self):
        """Test that extract_main_content successfully extracts content."""
        with patch('search_agent.modules.web_content_extractor.httpx.AsyncClient') as mock_client:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.text = """
            <html><body>
                <article>This is the main article content.</article>
                <div class="sidebar">This is sidebar content.</div>
            </body></html>
            """
            mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
            mock_response.raise_for_status = MagicMock()
            
            # Setup mock client
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value = mock_client_instance
            
            # Call the function
            result = await extract_main_content("https://example.com")
            
            # Verify the result
            assert result is not None
            assert "main article content" in result
            assert "sidebar content" not in result

    @pytest.mark.asyncio
    async def test_extract_main_content_http_error(self):
        """Test that extract_main_content handles HTTP errors correctly."""
        with patch('search_agent.modules.web_content_extractor.httpx.AsyncClient') as mock_client:
            # Setup mock client to raise an exception
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.get.side_effect = Exception("HTTP error")
            mock_client.return_value = mock_client_instance
            
            # Call the function and expect an exception
            with pytest.raises(ScrapingError) as excinfo:
                await extract_main_content("https://example.com")
            
            # Verify the exception message
            assert "Error extracting content" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_extract_main_content_no_content(self):
        """Test that extract_main_content handles pages with no extractable content."""
        with patch('search_agent.modules.web_content_extractor.httpx.AsyncClient') as mock_client:
            # Setup mock response with no meaningful content
            mock_response = MagicMock()
            mock_response.text = "<html><body></body></html>"
            mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
            mock_response.raise_for_status = MagicMock()
            
            # Setup mock client
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value = mock_client_instance
            
            # Call the function
            result = await extract_main_content("https://example.com")
            
            # Verify the result is None
            assert result is None
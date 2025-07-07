
"""Web content extraction module for the search agent system.

This module provides functionality to extract and clean the main textual content
from web pages using httpx for fetching and BeautifulSoup for parsing.
"""

import re
import httpx
import logging
from bs4 import BeautifulSoup
from typing import Optional, List
from urllib.parse import urlparse

from search_agent.core.exceptions import ScrapingError

# Configure logging
logger = logging.getLogger(__name__)

# Content priority selectors - ordered by likelihood of containing main content
CONTENT_TAGS = ['article', 'main', 'section', 'div']
CONTENT_CLASSES = [
    'content', 'main-content', 'post-content', 'article-body', 'entry-content',
    'post', 'article', 'blog-post', 'story', 'text', 'page-content',
    'main', 'body-content', 'entry', 'post-body'
]
CONTENT_IDS = [
    'content', 'main-content', 'post-content', 'article-body', 'entry-content',
    'main', 'article', 'post', 'story'
]

# Elements that typically don't contain main content
NOISE_SELECTORS = [
    'header', 'footer', 'nav', 'aside', 'sidebar', 
    '.sidebar', '.navigation', '.menu', '.nav', '.footer', '.header',
    '.comments', '.comment', '#comments', '#comment',
    '.advertisement', '.ads', '.ad', '#ad', '#ads',
    '.related', '.recommended', '.share', '.social'
]

async def extract_main_content(url: str) -> Optional[str]:
    """
    Fetches the content of a URL and extracts the main textual content.
    
    Args:
        url: The URL to fetch and extract content from
        
    Returns:
        The extracted and cleaned main content as a string, or None if no content could be extracted
        
    Raises:
        ScrapingError: If there's an error during fetching or parsing
    """
    try:
        # Parse the URL to validate it
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ScrapingError(f"Invalid URL format: {url}")
        
        # Set appropriate headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        logger.info(f"Fetching content from: {url}")
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Check if the response is HTML
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type.lower():
                logger.warning(f"URL {url} returned non-HTML content: {content_type}")
                
        # Parse the HTML
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if parsing was successful
            if not soup.html:
                logger.warning(f"BeautifulSoup couldn't parse HTML structure from {url}")
                # Try with a more lenient parser
                soup = BeautifulSoup(response.text, 'html5lib')
                if not soup.html:
                    raise ScrapingError(f"Failed to parse HTML content from {url}")
            
            # Remove noise elements first
            for selector in NOISE_SELECTORS:
                try:
                    for element in soup.select(selector):
                        element.decompose()
                except Exception as e:
                    logger.warning(f"Error removing noise element '{selector}': {e}")
                    # Continue with other selectors
                    continue
        except Exception as e:
            logger.error(f"BeautifulSoup parsing error for {url}: {e}")
            raise ScrapingError(f"HTML parsing error for {url}: {e}")
                
        # Try to find main content using different strategies
        main_content = extract_content_by_priority(soup)
        
        if not main_content:
            logger.warning(f"Could not find main content in {url} using priority selectors")
            # Fallback to extracting paragraphs
            paragraphs = soup.find_all('p')
            if paragraphs:
                main_content = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50)
        
        if not main_content:
            logger.warning(f"Could not extract any meaningful content from {url}")
            # Last resort: use body text
            if soup.body:
                # Clean the body first
                for script_or_style in soup.body(['script', 'style', 'noscript', 'iframe', 'svg']):
                    script_or_style.decompose()
                main_content = soup.body.get_text(separator=' ', strip=True)
        
        if not main_content:
            logger.error(f"No content could be extracted from {url}")
            return None
            
        # Clean the extracted content
        cleaned_content = clean_content(main_content)
        
        if not cleaned_content:
            logger.warning(f"Cleaning removed all content from {url}")
            return None
            
        logger.info(f"Successfully extracted {len(cleaned_content)} characters from {url}")
        return cleaned_content
        
    except httpx.TimeoutException as e:
        logger.error(f"Timeout while fetching {url}: {e}")
        raise ScrapingError(f"Timeout while fetching {url}: {e}")
    except httpx.RequestError as e:
        logger.error(f"Network or HTTP error while fetching {url}: {e}")
        raise ScrapingError(f"Network or HTTP error while fetching {url}: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} while fetching {url}: {e}")
        raise ScrapingError(f"HTTP error {e.response.status_code} while fetching {url}: {e}")
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {e}")
        raise ScrapingError(f"Error extracting content from {url}: {e}")


def extract_content_by_priority(soup: BeautifulSoup) -> str:
    """
    Extracts content from HTML using a priority-based approach.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML
        
    Returns:
        Extracted content as a string, or empty string if no content found
    """
    try:
        # Strategy 1: Look for elements with specific IDs
        for id_name in CONTENT_IDS:
            try:
                element = soup.find(id=id_name)
                if element:
                    # Clean the element
                    try:
                        for script_or_style in element(['script', 'style', 'noscript', 'iframe', 'svg']):
                            script_or_style.decompose()
                        content = element.get_text(separator=' ', strip=True)
                        if content:
                            logger.info(f"Found content using ID selector: {id_name}")
                            return content
                    except Exception as e:
                        logger.warning(f"Error cleaning element with ID '{id_name}': {e}")
            except Exception as e:
                logger.warning(f"Error finding element with ID '{id_name}': {e}")
                continue
        
        # Strategy 2: Look for elements with specific classes
        for class_name in CONTENT_CLASSES:
            try:
                elements = soup.find_all(class_=class_name)
                if elements:
                    texts = []
                    for element in elements:
                        try:
                            # Clean the element
                            for script_or_style in element(['script', 'style', 'noscript', 'iframe', 'svg']):
                                script_or_style.decompose()
                            text = element.get_text(separator=' ', strip=True)
                            if text:
                                texts.append(text)
                        except Exception as e:
                            logger.warning(f"Error processing element with class '{class_name}': {e}")
                    
                    if texts:
                        logger.info(f"Found content using class selector: {class_name}")
                        return " ".join(texts)
            except Exception as e:
                logger.warning(f"Error finding elements with class '{class_name}': {e}")
                continue
        
        # Strategy 3: Look for specific content tags
        for tag in CONTENT_TAGS:
            try:
                elements = soup.find_all(tag)
                if elements:
                    try:
                        # Find the element with the most text content
                        best_element = max(elements, key=lambda e: len(e.get_text(strip=True)), default=None)
                        if best_element and len(best_element.get_text(strip=True)) > 200:  # Minimum content length
                            # Clean the element
                            for script_or_style in best_element(['script', 'style', 'noscript', 'iframe', 'svg']):
                                script_or_style.decompose()
                            content = best_element.get_text(separator=' ', strip=True)
                            if content:
                                logger.info(f"Found content using tag selector: {tag}")
                                return content
                    except Exception as e:
                        logger.warning(f"Error processing elements with tag '{tag}': {e}")
            except Exception as e:
                logger.warning(f"Error finding elements with tag '{tag}': {e}")
                continue
        
        # Strategy 4: Look for the div with the most paragraph tags
        try:
            divs = soup.find_all('div')
            if divs:
                try:
                    div_with_most_paragraphs = max(divs, key=lambda d: len(d.find_all('p')), default=None)
                    if div_with_most_paragraphs and len(div_with_most_paragraphs.find_all('p')) > 3:
                        # Clean the element
                        for script_or_style in div_with_most_paragraphs(['script', 'style', 'noscript', 'iframe', 'svg']):
                            script_or_style.decompose()
                        content = div_with_most_paragraphs.get_text(separator=' ', strip=True)
                        if content:
                            logger.info("Found content using div with most paragraphs strategy")
                            return content
                except Exception as e:
                    logger.warning(f"Error processing divs with paragraphs: {e}")
        except Exception as e:
            logger.warning(f"Error finding divs: {e}")
        
        logger.warning("All content extraction strategies failed")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error in extract_content_by_priority: {e}")
        return ""


def clean_content(text: str) -> str:
    """
    Cleans the extracted text content.
    
    Args:
        text: The text to clean
        
    Returns:
        Cleaned text
    """
    try:
        if not text:
            return ""
            
        # Replace multiple newlines with a single space
        try:
            text = re.sub(r'\n+', ' ', text)
        except Exception as e:
            logger.warning(f"Error replacing newlines: {e}")
        
        # Replace multiple spaces with a single space
        try:
            text = re.sub(r'\s+', ' ', text)
        except Exception as e:
            logger.warning(f"Error replacing spaces: {e}")
        
        # Remove any remaining HTML tags
        try:
            text = re.sub(r'<[^>]+>', '', text)
        except Exception as e:
            logger.warning(f"Error removing HTML tags: {e}")
        
        # Remove common noise patterns
        noise_patterns = [
            r'Cookie Policy',
            r'Privacy Policy',
            r'Terms of Service',
            r'Accept Cookies',
            r'Use of Cookies',
            r'All Rights Reserved',
            r'Copyright \d{4}',
            r'Share this article',
            r'Share on \w+',
            r'Follow us',
            r'Subscribe to our newsletter',
            r'Sign up for our newsletter',
            r'Related Articles',
            r'You might also like',
            r'Recommended for you',
            r'Comments \(\d+\)',
            r'Click here',
            r'Read more',
            r'Learn more'
        ]
        
        for pattern in noise_patterns:
            try:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            except Exception as e:
                logger.warning(f"Error removing noise pattern '{pattern}': {e}")
                continue
        
        # Trim leading/trailing whitespace
        try:
            text = text.strip()
        except Exception as e:
            logger.warning(f"Error trimming whitespace: {e}")
        
        return text
    except Exception as e:
        logger.error(f"Unexpected error in clean_content: {e}")
        # Return the original text if cleaning fails
        return text if text else ""

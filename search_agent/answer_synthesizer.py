
import asyncio
import logging
import time
from typing import List, Optional, TYPE_CHECKING

from openai import APIError, RateLimitError, APIConnectionError, AuthenticationError

if TYPE_CHECKING:
    from search_agent.config import Configuration

from search_agent.core.exceptions import SearchAgentError
from search_agent.config import settings
from search_agent.utils import get_llm_client, get_model_name

# Configure logging
logger = logging.getLogger(__name__)

async def synthesize_answer(query: str, content_snippets: List[str], max_retries: int = 3, config: Optional['Configuration'] = None) -> Optional[str]:
    """
    Synthesizes an answer to the query using an LLM based on provided content snippets.
    
    Args:
        query: The user's query to answer
        content_snippets: List of text snippets from web pages to use as source material
        max_retries: Maximum number of retry attempts for transient errors
        config: Optional configuration object for LLM parameters
        
    Returns:
        Synthesized answer as a string, or None if synthesis fails after retries
    
    Raises:
        SearchAgentError: If there's a non-transient error or all retries fail
    """
    try:
        # Get the appropriate LLM client based on configuration
        client = get_llm_client()
        # Get the model name to use - prefer config over environment
        if config and hasattr(config, 'llm') and config.llm.model:
            model = get_model_name(config.llm.model)
        else:
            model = get_model_name(settings.LLM_SYNTHESIZER_MODEL)
    except SearchAgentError as e:
        raise SearchAgentError(f"Failed to configure LLM client for answer synthesis: {e}")

    # Combine content snippets into a single string
    combined_content = "\n\n---\n\n".join(content_snippets)

    # Construct the prompt for the LLM
    prompt = f"""You are an expert assistant tasked with synthesizing a concise and accurate answer to a user's query based on provided text snippets.

Here's the user's query:
"{query}"

Here are the text snippets from various web pages. Use ONLY the information present in these snippets to formulate your answer. Do NOT use any outside knowledge.

---
{combined_content}
---

Based on the query and the provided snippets, please synthesize a direct, concise, and factual answer. If the snippets do not contain enough information to answer the query, state that clearly.

Synthesized Answer:"""

    # Initialize retry parameters - prefer config over defaults
    if config and hasattr(config, 'advanced') and config.advanced.retry_count:
        max_retries = config.advanced.retry_count
    
    retry_count = 0
    base_delay = 1  # Start with a 1-second delay
    max_delay = 16  # Maximum delay between retries

    # Get LLM parameters from config or use defaults
    temperature = 0.2
    max_tokens = 500
    if config and hasattr(config, 'llm'):
        if config.llm.temperature is not None:
            temperature = config.llm.temperature
        if config.llm.max_tokens is not None:
            max_tokens = config.llm.max_tokens

    while retry_count <= max_retries:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Check if the answer is coherent and not an error message
            if not answer or "I don't have enough information" in answer and len(answer) < 50:
                logger.warning("LLM returned a potentially low-quality answer")
            
            return answer
            
        except RateLimitError as e:
            # Handle rate limit errors with exponential backoff
            if retry_count < max_retries:
                delay = min(max_delay, base_delay * (2 ** retry_count))
                logger.warning(f"Rate limit exceeded. Retrying in {delay} seconds. Error: {e}")
                await asyncio.sleep(delay)
                retry_count += 1
            else:
                logger.error(f"Rate limit exceeded and max retries reached: {e}")
                raise SearchAgentError(f"LLM rate limit exceeded after {max_retries} retries: {e}")
                
        except APIConnectionError as e:
            # Handle connection errors with exponential backoff
            if retry_count < max_retries:
                delay = min(max_delay, base_delay * (2 ** retry_count))
                logger.warning(f"API connection error. Retrying in {delay} seconds. Error: {e}")
                await asyncio.sleep(delay)
                retry_count += 1
            else:
                logger.error(f"API connection error and max retries reached: {e}")
                raise SearchAgentError(f"LLM API connection failed after {max_retries} retries: {e}")
                
        except APIError as e:
            # Handle general API errors with exponential backoff for 5xx errors
            if str(e).startswith("5") and retry_count < max_retries:
                delay = min(max_delay, base_delay * (2 ** retry_count))
                logger.warning(f"API server error. Retrying in {delay} seconds. Error: {e}")
                await asyncio.sleep(delay)
                retry_count += 1
            else:
                logger.error(f"API error: {e}")
                raise SearchAgentError(f"LLM API error: {e}")
                
        except AuthenticationError as e:
            # Authentication errors are not retryable
            logger.error(f"Authentication error: {e}")
            raise SearchAgentError(f"LLM authentication failed: {e}")
            
        except Exception as e:
            # Handle other unexpected errors
            logger.error(f"Unexpected error during answer synthesis: {e}")
            raise SearchAgentError(f"LLM answer synthesis failed: {e}")
    
    # This should not be reached due to the raise in the last retry, but just in case
    return None


import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, TYPE_CHECKING

import spacy
from openai import APIError, RateLimitError, APIConnectionError, AuthenticationError

if TYPE_CHECKING:
    from search_agent.config import Configuration

from search_agent.core.exceptions import SearchAgentError
from search_agent.config import settings
from search_agent.utils import get_llm_client, get_model_name

# Configure logging
logger = logging.getLogger(__name__)

async def evaluate_answer_quality(query: str, synthesized_answer: str, original_content: List[str], max_retries: int = 3, config: Optional['Configuration'] = None) -> Dict[str, Any]:
    """
    Evaluates the quality of a synthesized answer using an LLM and potentially NLP techniques.
    
    Args:
        query: The original user query
        synthesized_answer: The answer generated by the LLM
        original_content: List of text snippets from which the answer was synthesized
        max_retries: Maximum number of retry attempts for transient errors
        config: Optional configuration object for LLM parameters
        
    Returns:
        Dictionary of evaluation metrics (factual consistency score, relevance score, etc.)
    """
    evaluation_results = {
        "factual_consistency_score": 0.0,
        "relevance_score": 0.0,
        "completeness_score": 0.0,
        "conciseness_score": 0.0,
        "llm_feedback": None,
        "nlp_relevance_score": None
    }

    # Check if evaluation is disabled in config
    if config and hasattr(config, 'llm') and not config.llm.evaluation:
        evaluation_results["llm_feedback"] = "Evaluation skipped per configuration"
        return evaluation_results

    # LLM-based evaluation
    try:
        # Get the appropriate LLM client based on configuration
        client = get_llm_client()
        # Get the model name to use - prefer config over environment
        if config and hasattr(config, 'llm') and config.llm.model:
            model = get_model_name(config.llm.model)
        else:
            model = get_model_name(settings.LLM_EVALUATOR_MODEL)
    except SearchAgentError as e:
        logger.error(f"Failed to configure LLM client for answer evaluation: {e}")
        evaluation_results["llm_feedback"] = f"LLM evaluation configuration failed: {e}"
        # Continue with NLP evaluation even if LLM evaluation fails
    else:
        # This block is executed only if LLM client configuration was successful
        combined_original_content = "\n\n---\n\n".join(original_content)

        llm_prompt = f"""You are an expert evaluator of synthesized answers. Your task is to assess the quality of a synthesized answer based on the original query and the source content it was derived from.

Original Query:
"{query}"

Synthesized Answer:
"{synthesized_answer}"

Original Source Content:
---
{combined_original_content}
---

Evaluate the answer based on the following criteria, providing a score from 0.0 to 1.0 for each, and a brief textual feedback.

1.  **Factual Consistency (0.0-1.0):** How well does the synthesized answer align with the facts presented in the original source content? (1.0 = perfectly consistent, 0.0 = completely inconsistent or contains hallucinations)
2.  **Relevance (0.0-1.0):** How relevant is the synthesized answer to the original query? (1.0 = perfectly relevant, 0.0 = completely irrelevant)
3.  **Completeness (0.0-1.0):** How complete is the synthesized answer given the information available in the original source content? (1.0 = covers all key points from source relevant to query, 0.0 = misses crucial information)
4.  **Conciseness (0.0-1.0):** How concise is the synthesized answer without losing important information? (1.0 = perfectly concise, 0.0 = overly verbose or too brief)

Provide your evaluation in a JSON format with the following keys: `factual_consistency_score`, `relevance_score`, `completeness_score`, `conciseness_score`, and `llm_feedback` (a string).

Example JSON output:
{{"factual_consistency_score": 0.9, "relevance_score": 0.8, "completeness_score": 0.7, "conciseness_score": 0.9, "llm_feedback": "The answer is mostly accurate but could be more comprehensive."}}

JSON Evaluation:"""

        # Initialize retry parameters - prefer config over defaults
        if config and hasattr(config, 'advanced') and config.advanced.retry_count:
            max_retries = config.advanced.retry_count
        
        retry_count = 0
        base_delay = 1  # Start with a 1-second delay
        max_delay = 16  # Maximum delay between retries

        while retry_count <= max_retries:
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": llm_prompt}
                    ],
                    response_format={ "type": "json_object" },
                    max_tokens=500,
                    temperature=0.0,
                )
                llm_output = response.choices[0].message.content
                
                try:
                    # Try to parse as pure JSON first
                    parsed_llm_output = json.loads(llm_output)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON from markdown code blocks
                    import re
                    
                    # Look for JSON wrapped in markdown code blocks
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', llm_output, re.DOTALL)
                    if json_match and json_match.group(1):
                        try:
                            parsed_llm_output = json.loads(json_match.group(1))
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse extracted JSON from markdown: {e}. Extracted: {json_match.group(1)}")
                            evaluation_results["llm_feedback"] = f"Error parsing LLM evaluation output: {e}. Output: {llm_output}"
                            break
                    else:
                        logger.error(f"Failed to parse LLM output as JSON and no markdown JSON found. Output: {llm_output}")
                        evaluation_results["llm_feedback"] = f"Error parsing LLM evaluation output: No valid JSON found. Output: {llm_output}"
                        break
                
                # Extract the evaluation results
                evaluation_results["factual_consistency_score"] = parsed_llm_output.get("factual_consistency_score", 0.0)
                evaluation_results["relevance_score"] = parsed_llm_output.get("relevance_score", 0.0)
                evaluation_results["completeness_score"] = parsed_llm_output.get("completeness_score", 0.0)
                evaluation_results["conciseness_score"] = parsed_llm_output.get("conciseness_score", 0.0)
                evaluation_results["llm_feedback"] = parsed_llm_output.get("llm_feedback")
                
                # Break out of the retry loop on success
                break
                
            except RateLimitError as e:
                # Handle rate limit errors with exponential backoff
                if retry_count < max_retries:
                    delay = min(max_delay, base_delay * (2 ** retry_count))
                    logger.warning(f"Rate limit exceeded during evaluation. Retrying in {delay} seconds. Error: {e}")
                    await asyncio.sleep(delay)
                    retry_count += 1
                else:
                    logger.error(f"Rate limit exceeded and max retries reached during evaluation: {e}")
                    evaluation_results["llm_feedback"] = f"LLM rate limit exceeded after {max_retries} retries: {e}"
                    break
                    
            except APIConnectionError as e:
                # Handle connection errors with exponential backoff
                if retry_count < max_retries:
                    delay = min(max_delay, base_delay * (2 ** retry_count))
                    logger.warning(f"API connection error during evaluation. Retrying in {delay} seconds. Error: {e}")
                    await asyncio.sleep(delay)
                    retry_count += 1
                else:
                    logger.error(f"API connection error and max retries reached during evaluation: {e}")
                    evaluation_results["llm_feedback"] = f"LLM API connection failed after {max_retries} retries: {e}"
                    break
                    
            except APIError as e:
                # Handle general API errors with exponential backoff for 5xx errors
                if str(e).startswith("5") and retry_count < max_retries:
                    delay = min(max_delay, base_delay * (2 ** retry_count))
                    logger.warning(f"API server error during evaluation. Retrying in {delay} seconds. Error: {e}")
                    await asyncio.sleep(delay)
                    retry_count += 1
                else:
                    logger.error(f"API error during evaluation: {e}")
                    evaluation_results["llm_feedback"] = f"LLM API error: {e}"
                    break
                    
            except AuthenticationError as e:
                # Authentication errors are not retryable
                logger.error(f"Authentication error during evaluation: {e}")
                evaluation_results["llm_feedback"] = f"LLM authentication failed: {e}"
                break
                
            except Exception as e:
                # Handle other unexpected errors
                logger.error(f"Unexpected error during answer evaluation: {e}")
                evaluation_results["llm_feedback"] = f"LLM evaluation failed: {e}"
                break

    # NLP-based evaluation (Cosine Similarity)
    try:
        # Skip NLP evaluation if the answer is empty or very short
        if not synthesized_answer or len(synthesized_answer) < 10:
            logger.warning("Skipping NLP evaluation due to short or empty answer")
            evaluation_results["nlp_relevance_score"] = 0.0
        else:
            try:
                nlp = spacy.load("en_core_web_md")
                query_doc = nlp(query)
                answer_doc = nlp(synthesized_answer)
                
                # Ensure docs have vectors before calculating similarity
                if query_doc.has_vector and answer_doc.has_vector:
                    evaluation_results["nlp_relevance_score"] = query_doc.similarity(answer_doc)
                    logger.info(f"NLP relevance score: {evaluation_results['nlp_relevance_score']}")
                else:
                    logger.warning("Documents don't have vectors for similarity calculation")
                    evaluation_results["nlp_relevance_score"] = 0.0
            except OSError:
                logger.warning("spaCy model 'en_core_web_md' not found")
                evaluation_results["llm_feedback"] = (evaluation_results["llm_feedback"] or "") + \
                                                " spaCy model 'en_core_web_md' not found. Please install it with: python -m spacy download en_core_web_md"
    except Exception as e:
        logger.error(f"Error during NLP evaluation: {e}")
        evaluation_results["llm_feedback"] = (evaluation_results["llm_feedback"] or "") + f" NLP evaluation failed: {e}"

    return evaluation_results

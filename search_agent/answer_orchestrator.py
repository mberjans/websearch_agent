import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from urllib.parse import urlparse

import time
import typer
from pydantic import HttpUrl

if TYPE_CHECKING:
    from search_agent.config import Configuration

from search_agent.core.models import SearchModuleOutput, SearchResult, SynthesizedAnswer, AnswerEvaluationResult, FinalAnswerOutput
from search_agent.core.exceptions import SearchAgentError, ScrapingError
from search_agent.orchestrator import run_orchestration as run_search_orchestration
from search_agent.modules.web_content_extractor import extract_main_content
from search_agent.answer_synthesizer import synthesize_answer
from search_agent.answer_evaluator import evaluate_answer_quality

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The Typer app instance
app = typer.Typer()

# Constants for content quality assessment
MIN_CONTENT_LENGTH = 200  # Minimum number of characters for content to be considered useful
ERROR_PAGE_PATTERNS = [
    r"404\s+not\s+found",
    r"403\s+forbidden",
    r"500\s+internal\s+server\s+error",
    r"access\s+denied",
    r"page\s+not\s+found",
    r"content\s+not\s+available",
    r"this\s+page\s+isn't\s+available",
    r"sorry,\s+we\s+couldn't\s+find\s+that\s+page",
    r"the\s+requested\s+url\s+was\s+not\s+found",
    r"the\s+page\s+you\s+are\s+looking\s+for\s+does\s+not\s+exist"
]
IRRELEVANT_CONTENT_PATTERNS = [
    r"please\s+enable\s+javascript",
    r"please\s+enable\s+cookies",
    r"your\s+browser\s+is\s+out\s+of\s+date",
    r"captcha",
    r"robot\s+check",
    r"cloudflare",
    r"ddos\s+protection",
    r"security\s+check"
]


def is_low_quality_content(content: str) -> Tuple[bool, str]:
    """
    Checks if the extracted content is of low quality or represents an error page.
    
    Args:
        content: The extracted text content to check
        
    Returns:
        Tuple of (is_low_quality, reason)
    """
    if not content:
        return True, "Empty content"
        
    if len(content) < MIN_CONTENT_LENGTH:
        return True, f"Content too short ({len(content)} chars)"
        
    # Check for error page patterns
    for pattern in ERROR_PAGE_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True, f"Detected error page pattern: {pattern}"
            
    # Check for irrelevant content patterns
    for pattern in IRRELEVANT_CONTENT_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True, f"Detected irrelevant content pattern: {pattern}"
            
    return False, ""


async def orchestrate_answer_generation(query: str, num_links_to_parse: int = 3, config: Optional['Configuration'] = None) -> Dict[str, Any]:
    """
    Orchestrates the process of generating a synthesized answer from search results.
    
    Args:
        query: The user's query to answer
        num_links_to_parse: Number of top search results to parse for content
        
    Returns:
        Dictionary containing the synthesized answer, evaluation results, and metadata
    """
    start_time = time.perf_counter()
    
    synthesized_answer = ""
    source_urls = []
    extracted_contents = []
    filtered_contents = []
    evaluation_results = {}
    metadata = {
        "total_urls_found": 0,
        "urls_selected": 0,
        "extraction_success_count": 0,
        "extraction_failure_count": 0,
        "low_quality_content_count": 0,
        "search_execution_time": 0,
        "content_extraction_time": 0,
        "answer_synthesis_time": 0,
        "answer_evaluation_time": 0,
        "errors": []
    }

    try:
        # 1. Get initial search results from the existing search orchestrator
        logger.info(f"Initiating search for query: '{query}'")
        search_start_time = time.perf_counter()
        search_output: SearchModuleOutput = await run_search_orchestration(query, config)
        search_end_time = time.perf_counter()
        metadata["search_execution_time"] = search_end_time - search_start_time
        
        metadata["total_urls_found"] = len(search_output.results)
        logger.info(f"Search orchestration completed. Found {len(search_output.results)} results.")

        # 2. Select top N unique URLs from the search results
        selected_urls = []
        seen_urls = set()
        seen_domains = set()  # To ensure diversity of sources
        
        for result in search_output.results:
            if not result.url:
                continue
                
            url_str = str(result.url)
            
            # Skip if we've seen this URL before
            if url_str in seen_urls:
                continue
                
            # Parse the domain to ensure diversity
            domain = urlparse(url_str).netloc
            
            # If we already have 2 URLs from this domain, skip to ensure diversity
            if domain in seen_domains and sum(1 for u in selected_urls if domain in u) >= 2:
                continue
                
            selected_urls.append(url_str)
            seen_urls.add(url_str)
            seen_domains.add(domain)
            
            if len(selected_urls) >= num_links_to_parse:
                break
                
        metadata["urls_selected"] = len(selected_urls)
        logger.info(f"Selected {len(selected_urls)} unique URLs for content extraction.")

        # 3. For each selected URL, call web_content_extractor.extract_main_content
        extraction_tasks = []
        for url in selected_urls:
            extraction_tasks.append(extract_main_content(url))
        
        extraction_start_time = time.perf_counter()
        extracted_contents_raw = await asyncio.gather(*extraction_tasks, return_exceptions=True)
        extraction_end_time = time.perf_counter()
        metadata["content_extraction_time"] = extraction_end_time - extraction_start_time

        # Process and filter extracted content
        for i, content in enumerate(extracted_contents_raw):
            if isinstance(content, Exception):
                logger.warning(f"Failed to extract content from {selected_urls[i]}: {content}")
                metadata["extraction_failure_count"] += 1
                metadata["errors"].append(f"Extraction error for {selected_urls[i]}: {str(content)}")
            elif content:
                # Check content quality
                is_low_quality, reason = is_low_quality_content(content)
                
                if is_low_quality:
                    logger.warning(f"Low quality content from {selected_urls[i]}: {reason}")
                    metadata["low_quality_content_count"] += 1
                    metadata["errors"].append(f"Low quality content from {selected_urls[i]}: {reason}")
                else:
                    # Content passed quality checks
                    extracted_contents.append(content)
                    filtered_contents.append(content)
                    source_urls.append(selected_urls[i])
                    metadata["extraction_success_count"] += 1
            else:
                logger.warning(f"No content extracted from {selected_urls[i]}")
                metadata["extraction_failure_count"] += 1
                
        logger.info(f"Successfully extracted quality content from {len(filtered_contents)} URLs.")

        # Handle case where no valid content could be extracted
        if not filtered_contents:
            if extracted_contents:
                # We have some content, but it was all filtered out as low quality
                # Use it anyway as a fallback
                logger.warning("Using low quality content as fallback since no high-quality content was found")
                filtered_contents = extracted_contents
                metadata["errors"].append("Using low quality content as fallback")
            else:
                error_msg = "No content could be extracted from the selected search results."
                logger.error(error_msg)
                metadata["errors"].append(error_msg)
                return {
                    "query": query,
                    "synthesized_answer": f"I couldn't find any relevant information to answer your question about '{query}'. Please try rephrasing your query or providing more specific details.",
                    "source_urls": [],
                    "extracted_contents": [],
                    "evaluation_results": {
                        "factual_consistency_score": 0.0,
                        "relevance_score": 0.0,
                        "completeness_score": 0.0,
                        "conciseness_score": 0.0,
                        "llm_feedback": "No content could be extracted from search results."
                    },
                    "execution_time_seconds": time.perf_counter() - start_time,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "metadata": metadata
                }

        # 4. Call answer_synthesizer.synthesize_answer
        logger.info("Synthesizing answer using LLM...")
        synthesis_start_time = time.perf_counter()
        synthesized_answer = await synthesize_answer(query, filtered_contents, config=config)
        synthesis_end_time = time.perf_counter()
        metadata["answer_synthesis_time"] = synthesis_end_time - synthesis_start_time
        
        # Check if we got a valid answer
        if not synthesized_answer:
            logger.warning("LLM returned empty answer")
            synthesized_answer = f"I couldn't generate a good answer to your question about '{query}' based on the information I found. Please try rephrasing your query."
            metadata["errors"].append("LLM returned empty answer")
        elif len(synthesized_answer) < 50:
            logger.warning(f"LLM returned very short answer: '{synthesized_answer}'")
            metadata["errors"].append("LLM returned very short answer")
            
        logger.info("Answer synthesis completed.")

        # 5. Call answer_evaluator.evaluate_answer_quality
        logger.info("Evaluating synthesized answer quality...")
        evaluation_start_time = time.perf_counter()
        evaluation_results = await evaluate_answer_quality(query, synthesized_answer, filtered_contents, config=config)
        evaluation_end_time = time.perf_counter()
        metadata["answer_evaluation_time"] = evaluation_end_time - evaluation_start_time
        logger.info("Answer evaluation completed.")
        
        # Check evaluation results for potential issues
        if evaluation_results.get("factual_consistency_score", 0) < 0.5:
            logger.warning(f"Low factual consistency score: {evaluation_results.get('factual_consistency_score')}")
            metadata["errors"].append(f"Low factual consistency score: {evaluation_results.get('factual_consistency_score')}")
            
        if evaluation_results.get("relevance_score", 0) < 0.5:
            logger.warning(f"Low relevance score: {evaluation_results.get('relevance_score')}")
            metadata["errors"].append(f"Low relevance score: {evaluation_results.get('relevance_score')}")

    except SearchAgentError as e:
        logger.error(f"Answer orchestration failed: {e}")
        metadata["errors"].append(f"Answer orchestration error: {str(e)}")
        synthesized_answer = f"I encountered an error while trying to answer your question about '{query}': {e}"
    except Exception as e:
        logger.error(f"An unexpected error occurred during answer orchestration: {e}")
        metadata["errors"].append(f"Unexpected error: {str(e)}")
        synthesized_answer = f"I encountered an unexpected error while trying to answer your question about '{query}'. Please try again later."

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    # Construct the final output
    try:
        # Convert string URLs to HttpUrl objects for Pydantic model
        http_urls = []
        for url in source_urls:
            try:
                http_urls.append(HttpUrl(url))
            except Exception as e:
                logger.warning(f"Invalid URL format: {url}, error: {e}")
                
        # Create SynthesizedAnswer object
        answer_obj = SynthesizedAnswer(
            answer=synthesized_answer,
            source_urls=http_urls,
            timestamp_utc=datetime.now(timezone.utc),
            execution_time_seconds=metadata.get("answer_synthesis_time", 0)
        )
        
        # Create AnswerEvaluationResult object
        eval_obj = AnswerEvaluationResult(
            factual_consistency_score=evaluation_results.get("factual_consistency_score", 0.0),
            relevance_score=evaluation_results.get("relevance_score", 0.0),
            completeness_score=evaluation_results.get("completeness_score", 0.0),
            conciseness_score=evaluation_results.get("conciseness_score", 0.0),
            llm_feedback=evaluation_results.get("llm_feedback"),
            nlp_relevance_score=evaluation_results.get("nlp_relevance_score")
        )
        
        # Create FinalAnswerOutput object
        final_output = FinalAnswerOutput(
            query=query,
            synthesized_answer=answer_obj,
            evaluation_results=eval_obj,
            source_urls=http_urls,
            timestamp_utc=datetime.now(timezone.utc),
            execution_time_seconds=execution_time,
            metadata=metadata
        )
        
        # Convert to dictionary for JSON serialization
        result_dict = final_output.model_dump()
        
        # Add extracted contents to the result for debugging and analysis
        result_dict["extracted_contents"] = filtered_contents
        
        return result_dict
        
    except Exception as e:
        logger.error(f"Error creating structured output: {e}")
        # Fallback to simple dictionary if structured output fails
        return {
            "query": query,
            "synthesized_answer": synthesized_answer,
            "source_urls": source_urls,
            "extracted_contents": extracted_contents,
            "evaluation_results": evaluation_results,
            "execution_time_seconds": execution_time,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata
        }


@app.command("generate-answer")
def generate_answer_cli(
    query: str = typer.Argument(..., help="The query for which to generate an answer."),
    num_links: int = typer.Option(3, "--num-links", "-n", help="Number of top search results to parse for content.")
):
    """
    Generates a synthesized answer to a query by parsing top search results and using an LLM.
    """
    try:
        result = asyncio.run(orchestrate_answer_generation(query, num_links))
        import json
        typer.echo(json.dumps(result, indent=2, default=str))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)



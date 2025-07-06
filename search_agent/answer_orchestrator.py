
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

import typer

from search_agent.core.models import SearchModuleOutput, SearchResult
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


async def orchestrate_answer_generation(query: str, num_links_to_parse: int = 3) -> Dict[str, Any]:
    """
    Orchestrates the process of generating a synthesized answer from search results.
    """
    start_time = time.perf_counter()
    
    synthesized_answer = ""
    source_urls = []
    extracted_contents = []
    evaluation_results = {}

    try:
        # 1. Get initial search results from the existing search orchestrator
        logger.info(f"Initiating search for query: '{query}'")
        search_output: SearchModuleOutput = await run_search_orchestration(query)
        logger.info(f"Search orchestration completed. Found {len(search_output.results)} results.")

        # 2. Select top N unique URLs from the search results
        selected_urls = []
        seen_urls = set()
        for result in search_output.results:
            if result.url and str(result.url) not in seen_urls:
                selected_urls.append(str(result.url))
                seen_urls.add(str(result.url))
            if len(selected_urls) >= num_links_to_parse:
                break
        logger.info(f"Selected {len(selected_urls)} unique URLs for content extraction.")

        # 3. For each selected URL, call web_content_extractor.extract_main_content
        extraction_tasks = []
        for url in selected_urls:
            extraction_tasks.append(extract_main_content(url))
        
        extracted_contents_raw = await asyncio.gather(*extraction_tasks, return_exceptions=True)

        for i, content in enumerate(extracted_contents_raw):
            if isinstance(content, Exception):
                logger.warning(f"Failed to extract content from {selected_urls[i]}: {content}")
            elif content:
                extracted_contents.append(content)
                source_urls.append(selected_urls[i])
        logger.info(f"Successfully extracted content from {len(extracted_contents)} URLs.")

        if not extracted_contents:
            raise SearchAgentError("No content could be extracted from the selected search results.")

        # 4. Call answer_synthesizer.synthesize_answer
        logger.info("Synthesizing answer using LLM...")
        synthesized_answer = await synthesize_answer(query, extracted_contents)
        logger.info("Answer synthesis completed.")

        # 5. Call answer_evaluator.evaluate_answer_quality
        logger.info("Evaluating synthesized answer quality...")
        evaluation_results = await evaluate_answer_quality(query, synthesized_answer, extracted_contents)
        logger.info("Answer evaluation completed.")

    except SearchAgentError as e:
        logger.error(f"Answer orchestration failed: {e}")
        synthesized_answer = f"Error: {e}"
    except Exception as e:
        logger.error(f"An unexpected error occurred during answer orchestration: {e}")
        synthesized_answer = f"Error: An unexpected error occurred: {e}"

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    return {
        "query": query,
        "synthesized_answer": synthesized_answer,
        "source_urls": source_urls,
        "extracted_contents": extracted_contents, # For debugging/transparency
        "evaluation_results": evaluation_results,
        "execution_time_seconds": execution_time,
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }


@app.command()
def generate_answer(
    query: str = typer.Argument(..., help="The query for which to generate an answer."),
    num_links: int = typer.Option(3, "--num-links", "-n", help="Number of top search results to parse for content.")
):
    """
    Generates a synthesized answer to a query by parsing top search results and using an LLM.
    """
    try:
        result = asyncio.run(orchestrate_answer_generation(query, num_links))
        import json
        typer.echo(json.dumps(result, indent=2))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

"""Evaluator module for measuring speed and quality of search modules.

This module provides functionality to evaluate search modules on both speed and quality metrics.
It includes functions for measuring execution time, LLM-based quality evaluation, NLP-based
quality evaluation, and SQLite logging for evaluation results.
"""

import importlib
import sqlite3
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import typer
from openai import OpenAI
from search_agent.core.models import SearchModuleOutput
from search_agent.config import settings

# The Typer app instance
app = typer.Typer()


def measure_speed(module_name: str, query: str) -> float:
    """
    Measure the execution time of a search module.
    
    Args:
        module_name: Name of the search module (e.g., 'selenium_search', 'playwright_search')
        query: The search query to execute
        
    Returns:
        The execution time in seconds
        
    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the module doesn't have a search function
    """
    try:
        # Dynamically import the specified search module
        module = importlib.import_module(f"search_agent.modules.{module_name}")
        search_function = getattr(module, 'search')
        
        # Record start time using high-precision counter
        start_time = time.perf_counter()
        
        # Execute the search function
        if hasattr(search_function, '__call__'):
            # Check if it's an async function
            import asyncio
            import inspect
            
            if inspect.iscoroutinefunction(search_function):
                # Run async function
                result = asyncio.run(search_function(query))
            else:
                # Run sync function
                result = search_function(query)
        
        # Record end time
        end_time = time.perf_counter()
        
        # Calculate execution time
        execution_time = end_time - start_time
        
        return execution_time
        
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_name}': {e}")
    except AttributeError as e:
        raise AttributeError(f"Module '{module_name}' does not have a 'search' function: {e}")


def evaluate_quality_llm(search_output: SearchModuleOutput) -> int:
    """
    Evaluate the quality and relevance of search results using an LLM.
    
    Args:
        search_output: The SearchModuleOutput object containing search results
        
    Returns:
        An integer score from 1-10 representing the quality/relevance of results
        
    Raises:
        ValueError: If API key is not configured or LLM response is invalid
        Exception: If API call fails
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured in settings")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Format search results for the prompt
    formatted_results = ""
    for i, result in enumerate(search_output.results, 1):
        formatted_results += f"{i}. Title: {result.title}\n"
        formatted_results += f"   URL: {result.url}\n"
        formatted_results += f"   Snippet: {result.snippet}\n\n"
    
    # Engineer a clear, specific prompt for quality evaluation
    prompt = f"""You are an expert search quality analyst. Your task is to evaluate a list of search results based on their relevance and usefulness for the given user query.

Please provide a single integer score from 1 to 10 based on the following scale:
1: Completely irrelevant or spam.
5: Partially relevant, but does not directly answer the user's intent.
10: Perfectly relevant, high-quality, and directly addresses the user's intent.

The user's query is:
"{search_output.query}"

Here are the search results to evaluate:
---
{formatted_results}---

Based on the query and the provided results, what is the overall relevance score?
Provide only the integer score and nothing else.

Relevance Score (1-10):"""

    try:
        # Call the LLM API
        response = client.chat.completions.create(
            model=settings.LLM_EVALUATOR_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.0  # Use deterministic responses
        )
        
        # Extract and parse the score
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract integer from response
        try:
            score = int(response_text)
            if 1 <= score <= 10:
                return score
            else:
                raise ValueError(f"Score {score} is outside valid range 1-10")
        except ValueError:
            # Try to extract first number from response if direct parsing fails
            import re
            numbers = re.findall(r'\d+', response_text)
            if numbers:
                score = int(numbers[0])
                if 1 <= score <= 10:
                    return score
            
            raise ValueError(f"Could not parse valid score from LLM response: '{response_text}'")
            
    except Exception as e:
        raise Exception(f"LLM API call failed: {e}")


def setup_database() -> None:
    """
    Initialize the SQLite database for storing evaluation results.
    Creates the evaluation_log table if it doesn't exist.
    """
    db_path = settings.EVALUATION_DB_PATH
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create the evaluation_log table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp_utc TEXT NOT NULL,
                module_name TEXT NOT NULL,
                query TEXT NOT NULL,
                execution_time_seconds REAL NOT NULL,
                llm_quality_score INTEGER,
                nlp_similarity_score REAL,
                result_count INTEGER NOT NULL,
                was_successful INTEGER NOT NULL,
                error_message TEXT,
                raw_output_json TEXT
            )
        """)
        
        conn.commit()


def log_evaluation(
    module_name: str,
    query: str,
    execution_time_seconds: float,
    result_count: int,
    was_successful: bool,
    llm_quality_score: Optional[int] = None,
    nlp_similarity_score: Optional[float] = None,
    error_message: Optional[str] = None,
    raw_output_json: Optional[str] = None
) -> None:
    """
    Log evaluation results to the SQLite database.
    
    Args:
        module_name: Name of the search module
        query: The search query that was executed
        execution_time_seconds: Time taken to execute the search
        result_count: Number of results returned
        was_successful: Whether the search completed without errors
        llm_quality_score: Optional LLM-based quality score (1-10)
        nlp_similarity_score: Optional NLP-based similarity score (0-1)
        error_message: Optional error message if search failed
        raw_output_json: Optional raw JSON output from the search module
    """
    db_path = settings.EVALUATION_DB_PATH
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Insert evaluation record
        cursor.execute("""
            INSERT INTO evaluation_log (
                run_timestamp_utc, module_name, query, execution_time_seconds,
                llm_quality_score, nlp_similarity_score, result_count,
                was_successful, error_message, raw_output_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            module_name,
            query,
            execution_time_seconds,
            llm_quality_score,
            nlp_similarity_score,
            result_count,
            1 if was_successful else 0,
            error_message,
            raw_output_json
        ))
        
        conn.commit()


@app.command()
def evaluate_speed(
    module_name: str = typer.Argument(..., help="Name of the search module to evaluate"),
    query: str = typer.Argument(..., help="Search query to execute")
):
    """
    Evaluate the speed of a search module.
    """
    try:
        execution_time = measure_speed(module_name, query)
        
        typer.echo(f"Module: {module_name}")
        typer.echo(f"Query: {query}")
        typer.echo(f"Execution time: {execution_time:.4f} seconds")
        
        # Log the result
        log_evaluation(
            module_name=module_name,
            query=query,
            execution_time_seconds=execution_time,
            result_count=0,  # We don't have result count in speed-only evaluation
            was_successful=True
        )
        
    except Exception as e:
        typer.echo(f"Error evaluating module '{module_name}': {e}", err=True)
        
        # Log the error
        log_evaluation(
            module_name=module_name,
            query=query,
            execution_time_seconds=0.0,
            result_count=0,
            was_successful=False,
            error_message=str(e)
        )
        
        raise typer.Exit(1)


@app.command()
def init_db():
    """
    Initialize the evaluation database.
    """
    try:
        setup_database()
        typer.echo(f"Database initialized at: {settings.EVALUATION_DB_PATH}")
    except Exception as e:
        typer.echo(f"Error initializing database: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
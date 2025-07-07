#!/usr/bin/env python3
"""
Clinical Metabolomics Oracle Web Search Agent

A command-line tool for searching the web and generating answers to medical and scientific queries.
"""

import asyncio
import logging
import os
import sys
import typer
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from search_agent.config import Configuration
from search_agent.answer_orchestrator import orchestrate_answer_generation
from search_agent.core.exceptions import SearchAgentError
from search_agent import __version__

# Create the Typer app
app = typer.Typer(
    name="websearch-agent",
    help=f"Clinical Metabolomics Oracle Web Search Agent (v{__version__})",
    add_completion=False
)


def validate_query(query: str) -> None:
    """Validate the search query."""
    if not query or not query.strip():
        raise typer.BadParameter("Query cannot be empty")
    
    if len(query.strip()) < 3:
        raise typer.BadParameter("Query must be at least 3 characters long")
    
    if len(query.strip()) > 500:
        raise typer.BadParameter("Query must be less than 500 characters")


def validate_output_dir(output_dir: Optional[str]) -> None:
    """Validate the output directory."""
    if output_dir:
        # Check if the directory is writable
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            test_file = Path(output_dir) / ".test_write"
            test_file.touch()
            test_file.unlink()
        except (OSError, PermissionError) as e:
            raise typer.BadParameter(f"Output directory '{output_dir}' is not writable: {e}")


def validate_project_name(project_name: Optional[str]) -> None:
    """Validate the project name."""
    if project_name:
        # Check for valid characters (alphanumeric, underscore, hyphen)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', project_name):
            raise typer.BadParameter("Project name can only contain letters, numbers, underscores, and hyphens")
        
        if len(project_name) > 50:
            raise typer.BadParameter("Project name must be less than 50 characters")


def validate_output_file(output_file: Optional[str]) -> None:
    """Validate the output file name."""
    if output_file:
        # Check for valid characters
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', output_file):
            raise typer.BadParameter("Output file name can only contain letters, numbers, underscores, and hyphens")
        
        if len(output_file) > 100:
            raise typer.BadParameter("Output file name must be less than 100 characters")


def setup_logging(verbose: bool = False, quiet: bool = False, debug: bool = False) -> None:
    """Configure logging based on verbosity level."""
    if quiet:
        logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')
    elif debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    elif verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')


def prepare_output_path(config: Configuration) -> str:
    """Prepare the output directory and return the full output path."""
    if config.output.path:
        output_path = config.output.path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return output_path
    
    # Create output directory structure
    output_dir = os.path.join(
        config.output.directory,
        config.output.project_name
    )
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{config.output.file}_{timestamp}.json"
    
    return os.path.join(output_dir, filename)


def create_output_directory_structure(base_dir: str, project_name: str) -> str:
    """Create the output directory structure and return the project directory path."""
    project_dir = os.path.join(base_dir, project_name)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir


def generate_output_filename(base_name: str, extension: str = "json") -> str:
    """Generate a timestamped filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"


@app.command()
def search(
    # Core arguments
    query: str = typer.Argument(..., help="The question to search for"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Directory to save results"),
    output_file: Optional[str] = typer.Option(None, "--output-file", "-f", help="Base name for output files"),
    output_path: Optional[str] = typer.Option(None, "--output-path", "-p", help="Absolute path for output file"),
    project_name: Optional[str] = typer.Option(None, "--project-name", "-n", help="Project name for organizing results"),
    
    # Search configuration
    search_provider: Optional[str] = typer.Option(None, "--search-provider", help="Search provider(s) to use"),
    max_results: Optional[int] = typer.Option(None, "--max-results", "-m", help="Maximum search results"),
    max_urls: Optional[int] = typer.Option(None, "--max-urls", "-u", help="Maximum URLs to extract"),
    timeout: Optional[int] = typer.Option(None, "--timeout", "-t", help="Timeout for operations (seconds)"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable caching of search results"),
    force_refresh: bool = typer.Option(False, "--force-refresh", help="Force refresh of cached results"),
    
    # LLM configuration
    llm_provider: Optional[str] = typer.Option(None, "--llm-provider", help="LLM API provider to use"),
    llm_model: Optional[str] = typer.Option(None, "--llm-model", help="LLM model to use"),
    temperature: Optional[float] = typer.Option(None, "--temperature", help="Temperature parameter for LLM"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Maximum tokens for LLM response"),
    no_evaluation: bool = typer.Option(False, "--no-evaluation", help="Skip answer quality evaluation"),
    
    # Advanced options
    config_file: Optional[str] = typer.Option(None, "--config-file", help="Path to custom configuration file"),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="Proxy URL for web requests"),
    user_agent: Optional[str] = typer.Option(None, "--user-agent", help="Custom user agent for web requests"),
    retry_count: Optional[int] = typer.Option(None, "--retry-count", help="Number of retries for failed operations"),
    extract_images: bool = typer.Option(False, "--extract-images", help="Extract and include images in results"),
    save_html: bool = typer.Option(False, "--save-html", help="Save raw HTML of extracted pages"),
    
    # Logging configuration
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress all output except errors"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
):
    """
    Search the web and generate a synthesized answer to a query.
    
    This command searches multiple sources, extracts content, and uses LLM to generate
    a comprehensive answer to your query.
    """
    
    # Validate core arguments
    validate_query(query)
    validate_output_dir(output_dir)
    validate_project_name(project_name)
    validate_output_file(output_file)
    
    # Set up logging first
    setup_logging(verbose=verbose, quiet=quiet, debug=debug)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        if config_file:
            logger.info(f"Loading configuration from file: {config_file}")
            config = Configuration.from_file(config_file, query)
        else:
            logger.info("Loading configuration from environment variables")
            config = Configuration.from_env(query)
        
        # Override configuration with command-line arguments
        if output_dir:
            config.output.directory = output_dir
        if output_file:
            config.output.file = output_file
        if output_path:
            config.output.path = output_path
        if project_name:
            config.output.project_name = project_name
            
        if search_provider:
            config.search.provider = search_provider
        if max_results:
            config.search.max_results = max_results
        if max_urls:
            config.search.max_urls = max_urls
        if timeout:
            config.search.timeout = timeout
        if no_cache:
            config.search.cache = False
        if force_refresh:
            config.search.force_refresh = force_refresh
            
        if llm_provider:
            config.llm.provider = llm_provider
        if llm_model:
            config.llm.model = llm_model
        if temperature is not None:
            config.llm.temperature = temperature
        if max_tokens:
            config.llm.max_tokens = max_tokens
        if no_evaluation:
            config.llm.evaluation = False
            
        if proxy:
            config.advanced.proxy = proxy
        if user_agent:
            config.advanced.user_agent = user_agent
        if retry_count:
            config.advanced.retry_count = retry_count
        if extract_images:
            config.advanced.extract_images = extract_images
        if save_html:
            config.advanced.save_html = save_html
        if debug:
            config.advanced.debug = debug
        
        # Set environment variables based on configuration
        config.set_env_vars()
        
        # Prepare output path
        output_path = prepare_output_path(config)
        logger.info(f"Output will be saved to: {output_path}")
        
        # Display configuration summary
        if not quiet:
            typer.echo(f"Query: {config.query}")
            typer.echo(f"Search Provider: {config.search.provider}")
            typer.echo(f"Max Results: {config.search.max_results}")
            typer.echo(f"LLM Model: {config.llm.model}")
            typer.echo(f"Output Path: {output_path}")
            typer.echo("Starting search and answer generation...")
        
        # Run the answer orchestration
        logger.info("Starting answer orchestration")
        result = asyncio.run(orchestrate_answer_generation(config.query, config.search.max_urls))
        
        # Save result to file
        import json
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        if not quiet:
            typer.echo(f"✓ Answer generated successfully!")
            typer.echo(f"✓ Results saved to: {output_path}")
            typer.echo(f"\nSynthesized Answer:")
            typer.echo("-" * 60)
            typer.echo(result.get('synthesized_answer', 'No answer generated'))
        
        # Display evaluation results if available
        if config.llm.evaluation and result.get('evaluation_results') and not quiet:
            eval_results = result['evaluation_results']
            typer.echo(f"\nAnswer Quality Evaluation:")
            typer.echo("-" * 60)
            typer.echo(f"Factual Consistency: {eval_results.get('factual_consistency_score', 'N/A')}")
            typer.echo(f"Relevance: {eval_results.get('relevance_score', 'N/A')}")
            typer.echo(f"Completeness: {eval_results.get('completeness_score', 'N/A')}")
            typer.echo(f"Conciseness: {eval_results.get('conciseness_score', 'N/A')}")
        
        logger.info("Answer orchestration completed successfully")
        
    except SearchAgentError as e:
        logger.error(f"Search agent error: {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        typer.echo("Operation cancelled by user.", err=True)
        raise typer.Exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        typer.echo(f"Unexpected error: {e}", err=True)
        if debug:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def version():
    """Display version information."""
    typer.echo("Clinical Metabolomics Oracle Web Search Agent v0.1.0")
    typer.echo("A modular, extensible web search agent system")


if __name__ == "__main__":
    app()
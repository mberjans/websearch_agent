# Clinical Metabolomics Oracle Web Search Agent - Input Arguments Implementation Plan

This document outlines a comprehensive plan for implementing command-line arguments and configuration options in the Clinical Metabolomics Oracle Web Search Agent.

## Table of Contents
1. [Current State Analysis](#current-state-analysis)
2. [Implementation Goals](#implementation-goals)
3. [Argument Categories](#argument-categories)
4. [Implementation Steps](#implementation-steps)
5. [Code Changes](#code-changes)
6. [Testing Plan](#testing-plan)
7. [Documentation Updates](#documentation-updates)
8. [Future Extensions](#future-extensions)

## Current State Analysis

### Existing CLI Structure
- The project uses Typer for CLI functionality
- Basic CLI command `generate-answer` in `answer_orchestrator.py`
- Limited parameters:
  - `query`: The query to search for (required argument)
  - `num_links`: Number of top search results to parse (optional, default: 3)
- Individual search modules have their own CLI commands for testing
- Duplicate command definition in `answer_orchestrator.py` needs to be fixed

### Configuration Management
- Environment variables are used for configuration in `config.py`
- No centralized configuration object passed to components
- No configuration file support

### Limitations
- No way to select specific search providers from CLI
- No control over output file location/naming
- No LLM provider/model selection from CLI
- No advanced options like proxy, user-agent, etc.
- No configuration file support

## Implementation Goals

1. Create a comprehensive CLI that exposes all functionality
2. Implement configuration file support for complex configurations
3. Ensure backward compatibility with existing code
4. Make the system more modular and configurable
5. Improve error handling and user feedback
6. Provide clear documentation for all options

## Argument Categories

### Core Arguments

| Argument | Description | Default | Implementation |
|----------|-------------|---------|----------------|
| `--query`, `-q` | The question to search for | None (Required) | Update existing parameter |
| `--output-dir`, `-o` | Directory to save results | `./output` | New parameter |
| `--output-file`, `-f` | Base name for output files | `answer_result` | New parameter |
| `--output-path`, `-p` | Absolute path for output file | None | New parameter |
| `--project-name`, `-n` | Project name for organizing results | `default_project` | New parameter |
| `--verbose`, `-v` | Enable verbose logging | `False` | New parameter |
| `--quiet` | Suppress all output except errors | `False` | New parameter |

### Search Configuration

| Argument | Description | Default | Implementation |
|----------|-------------|---------|----------------|
| `--search-provider` | Search provider(s) to use | `all` | New parameter |
| `--max-results`, `-m` | Maximum search results | `10` | Rename from `num_links` |
| `--max-urls`, `-u` | Maximum URLs to extract | `3` | New parameter |
| `--timeout`, `-t` | Timeout for operations (seconds) | `30` | New parameter |
| `--no-cache` | Disable caching of search results | `False` | New parameter |
| `--force-refresh` | Force refresh of cached results | `False` | New parameter |

### LLM Configuration

| Argument | Description | Default | Implementation |
|----------|-------------|---------|----------------|
| `--llm-provider` | LLM API provider to use | `openrouter` | New parameter |
| `--llm-model` | LLM model to use | `gpt-4o-mini` | New parameter |
| `--temperature` | Temperature parameter for LLM | `0.1` | New parameter |
| `--max-tokens` | Maximum tokens for LLM response | `1024` | New parameter |
| `--no-evaluation` | Skip answer quality evaluation | `False` | New parameter |

### Advanced Options

| Argument | Description | Default | Implementation |
|----------|-------------|---------|----------------|
| `--config-file` | Path to custom configuration file | `None` | New parameter |
| `--proxy` | Proxy URL for web requests | `None` | New parameter |
| `--user-agent` | Custom user agent for web requests | `None` | New parameter |
| `--retry-count` | Number of retries for failed operations | `3` | New parameter |
| `--extract-images` | Extract and include images in results | `False` | New parameter |
| `--save-html` | Save raw HTML of extracted pages | `False` | New parameter |
| `--debug` | Enable debug mode | `False` | New parameter |

## Implementation Steps

### 1. Fix Duplicate Command Definition
- Remove the duplicate `generate-answer` command in `answer_orchestrator.py`

### 2. Create Configuration Class
- Create a `Configuration` class in `config.py` to centralize configuration
- Include all configurable parameters with default values
- Add methods to load from environment variables, command-line arguments, and configuration files
- Implement validation for configuration values

### 3. Update Main CLI Script
- Create a new main script `websearch_agent.py` in the project root
- Implement all command-line arguments using Typer
- Add configuration file support using PyYAML
- Implement proper error handling and user feedback

### 4. Update Orchestrator Functions
- Modify `orchestrate_answer_generation` to accept a configuration object
- Update all dependent functions to use the configuration object
- Ensure backward compatibility with existing code

### 5. Update Search Modules
- Modify search modules to accept configuration parameters
- Implement provider selection based on configuration
- Add support for advanced options like proxy, user-agent, etc.

### 6. Update Answer Generation Components
- Modify answer synthesizer to use configuration parameters
- Update answer evaluator to respect the `no-evaluation` flag
- Implement LLM provider/model selection

### 7. Implement Output Management
- Create functions to manage output directories and files
- Implement project-based organization of results
- Add support for different output formats (JSON, Markdown, etc.)

### 8. Add Configuration File Support
- Implement YAML configuration file parsing
- Create a template configuration file
- Add validation for configuration files

### 9. Update Documentation
- Update README.md with CLI usage information
- Create comprehensive documentation for all options
- Add examples for common use cases

### 10. Add Tests
- Create unit tests for configuration parsing
- Add integration tests for CLI functionality
- Implement end-to-end tests for the full workflow

## Code Changes

### 1. Configuration Class in `config.py`

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union, Dict, Any
import os
import yaml
from pathlib import Path

class SearchConfig(BaseModel):
    provider: str = "all"
    max_results: int = 10
    max_urls: int = 3
    timeout: int = 30
    cache: bool = True
    force_refresh: bool = False

class LLMConfig(BaseModel):
    provider: str = "openrouter"
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 1024
    evaluation: bool = True

class OutputConfig(BaseModel):
    directory: str = "./output"
    file: str = "answer_result"
    path: Optional[str] = None
    project_name: str = "default_project"

class AdvancedConfig(BaseModel):
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    retry_count: int = 3
    extract_images: bool = False
    save_html: bool = False
    debug: bool = False

class Configuration(BaseModel):
    query: str
    search: SearchConfig = Field(default_factory=SearchConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    advanced: AdvancedConfig = Field(default_factory=AdvancedConfig)
    
    @classmethod
    def from_env(cls, query: str) -> "Configuration":
        """Create configuration from environment variables."""
        return cls(
            query=query,
            search=SearchConfig(
                provider=os.getenv("SEARCH_PROVIDER", "all"),
                max_results=int(os.getenv("MAX_SEARCH_RESULTS", "10")),
                max_urls=int(os.getenv("MAX_URLS_TO_EXTRACT", "3")),
                timeout=int(os.getenv("SEARCH_TIMEOUT", "30")),
                cache=os.getenv("USE_CACHE", "true").lower() == "true",
                force_refresh=os.getenv("FORCE_REFRESH", "false").lower() == "true"
            ),
            llm=LLMConfig(
                provider=os.getenv("LLM_PROVIDER", "openrouter"),
                model=os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
                evaluation=os.getenv("PERFORM_EVALUATION", "true").lower() == "true"
            ),
            output=OutputConfig(
                directory=os.getenv("OUTPUT_DIRECTORY", "./output"),
                file=os.getenv("OUTPUT_FILE", "answer_result"),
                path=os.getenv("OUTPUT_PATH"),
                project_name=os.getenv("PROJECT_NAME", "default_project")
            ),
            advanced=AdvancedConfig(
                proxy=os.getenv("HTTP_PROXY"),
                user_agent=os.getenv("USER_AGENT"),
                retry_count=int(os.getenv("RETRY_COUNT", "3")),
                extract_images=os.getenv("EXTRACT_IMAGES", "false").lower() == "true",
                save_html=os.getenv("SAVE_HTML", "false").lower() == "true",
                debug=os.getenv("DEBUG", "false").lower() == "true"
            )
        )
    
    @classmethod
    def from_file(cls, config_path: str, query: Optional[str] = None) -> "Configuration":
        """Load configuration from a YAML file."""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # If query is provided, override the one in the config file
        if query:
            config_data["query"] = query
            
        return cls(**config_data)
    
    def to_env_vars(self) -> Dict[str, str]:
        """Convert configuration to environment variables."""
        env_vars = {
            "SEARCH_PROVIDER": self.search.provider,
            "MAX_SEARCH_RESULTS": str(self.search.max_results),
            "MAX_URLS_TO_EXTRACT": str(self.search.max_urls),
            "SEARCH_TIMEOUT": str(self.search.timeout),
            "USE_CACHE": str(self.search.cache).lower(),
            "FORCE_REFRESH": str(self.search.force_refresh).lower(),
            
            "LLM_PROVIDER": self.llm.provider,
            "DEFAULT_LLM_MODEL": self.llm.model,
            "LLM_TEMPERATURE": str(self.llm.temperature),
            "LLM_MAX_TOKENS": str(self.llm.max_tokens),
            "PERFORM_EVALUATION": str(self.llm.evaluation).lower(),
            
            "OUTPUT_DIRECTORY": self.output.directory,
            "OUTPUT_FILE": self.output.file,
            "PROJECT_NAME": self.output.project_name
        }
        
        if self.output.path:
            env_vars["OUTPUT_PATH"] = self.output.path
            
        if self.advanced.proxy:
            env_vars["HTTP_PROXY"] = self.advanced.proxy
            env_vars["HTTPS_PROXY"] = self.advanced.proxy
            
        if self.advanced.user_agent:
            env_vars["USER_AGENT"] = self.advanced.user_agent
            
        env_vars["RETRY_COUNT"] = str(self.advanced.retry_count)
        env_vars["EXTRACT_IMAGES"] = str(self.advanced.extract_images).lower()
        env_vars["SAVE_HTML"] = str(self.advanced.save_html).lower()
        env_vars["DEBUG"] = str(self.advanced.debug).lower()
        
        return env_vars
    
    def set_env_vars(self) -> None:
        """Set environment variables based on configuration."""
        env_vars = self.to_env_vars()
        for key, value in env_vars.items():
            os.environ[key] = value
```

### 2. Main CLI Script `websearch_agent.py`

```python
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

# Create the Typer app
app = typer.Typer(
    name="websearch-agent",
    help="Clinical Metabolomics Oracle Web Search Agent",
    add_completion=False
)

def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging based on verbosity level."""
    if quiet:
        logging.basicConfig(level=logging.ERROR)
    elif verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

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

async def run_search(config: Configuration, output_path: str) -> None:
    """Run the search and answer generation process."""
    try:
        # Set environment variables for backward compatibility
        config.set_env_vars()
        
        # Run the answer generation pipeline
        result = await orchestrate_answer_generation(
            config.query, 
            config.search.max_urls
        )
        
        # Save the result to the output file
        import json
        
        # Convert non-serializable objects to strings for JSON serialization
        def convert_for_json(obj):
            if hasattr(obj, '__class__') and obj.__class__.__name__ == 'HttpUrl':
                return str(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, default=convert_for_json)
        
        logging.info(f"Result saved to {output_path}")
        
        # Print the answer to stdout
        print("\n" + "="*80)
        print(f"QUERY: {config.query}")
        print("="*80)
        
        print("\nANSWER:")
        print("-"*80)
        if isinstance(result, dict) and "synthesized_answer" in result:
            if isinstance(result["synthesized_answer"], dict):
                print(result["synthesized_answer"].get("answer", "No answer generated"))
            else:
                print(result["synthesized_answer"])
        else:
            print("No answer generated")
        
        print("\nSOURCES:")
        print("-"*80)
        if isinstance(result, dict) and "source_urls" in result:
            for url in result["source_urls"]:
                print(f"- {url}")
        else:
            print("No sources found")
        
    except Exception as e:
        logging.error(f"Error during search: {e}", exc_info=True)
        raise typer.Exit(code=1)

@app.command("search")
def search(
    # Core arguments
    query: str = typer.Option(..., "--query", "-q", help="The question to search for"),
    output_dir: str = typer.Option("./output", "--output-dir", "-o", help="Directory to save results"),
    output_file: str = typer.Option("answer_result", "--output-file", "-f", help="Base name for output files"),
    output_path: Optional[str] = typer.Option(None, "--output-path", "-p", help="Absolute path for output file"),
    project_name: str = typer.Option("default_project", "--project-name", "-n", help="Project name for organizing results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress all output except errors"),
    
    # Search configuration
    search_provider: str = typer.Option("all", "--search-provider", help="Search provider(s) to use (comma-separated)"),
    max_results: int = typer.Option(10, "--max-results", "-m", help="Maximum number of search results to retrieve"),
    max_urls: int = typer.Option(3, "--max-urls", "-u", help="Maximum number of URLs to extract content from"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout for search and extraction operations (seconds)"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable caching of search results"),
    force_refresh: bool = typer.Option(False, "--force-refresh", help="Force refresh of cached results"),
    
    # LLM configuration
    llm_provider: str = typer.Option("openrouter", "--llm-provider", help="LLM API provider to use"),
    llm_model: str = typer.Option("gpt-4o-mini", "--llm-model", help="LLM model to use"),
    temperature: float = typer.Option(0.1, "--temperature", help="Temperature parameter for LLM"),
    max_tokens: int = typer.Option(1024, "--max-tokens", help="Maximum tokens for LLM response"),
    no_evaluation: bool = typer.Option(False, "--no-evaluation", help="Skip answer quality evaluation"),
    
    # Advanced options
    config_file: Optional[str] = typer.Option(None, "--config-file", help="Path to custom configuration file"),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="Proxy URL for web requests"),
    user_agent: Optional[str] = typer.Option(None, "--user-agent", help="Custom user agent for web requests"),
    retry_count: int = typer.Option(3, "--retry-count", help="Number of retries for failed operations"),
    extract_images: bool = typer.Option(False, "--extract-images", help="Extract and include images in results"),
    save_html: bool = typer.Option(False, "--save-html", help="Save raw HTML of extracted pages"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
):
    """
    Search the web and generate an answer to a query.
    """
    try:
        # Set up logging
        setup_logging(verbose=verbose, quiet=quiet)
        
        # Load configuration
        if config_file:
            try:
                config = Configuration.from_file(config_file, query)
                logging.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logging.error(f"Error loading configuration file: {e}")
                raise typer.Exit(code=1)
        else:
            # Create configuration from command-line arguments
            config = Configuration(
                query=query,
                search={
                    "provider": search_provider,
                    "max_results": max_results,
                    "max_urls": max_urls,
                    "timeout": timeout,
                    "cache": not no_cache,
                    "force_refresh": force_refresh
                },
                llm={
                    "provider": llm_provider,
                    "model": llm_model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "evaluation": not no_evaluation
                },
                output={
                    "directory": output_dir,
                    "file": output_file,
                    "path": output_path,
                    "project_name": project_name
                },
                advanced={
                    "proxy": proxy,
                    "user_agent": user_agent,
                    "retry_count": retry_count,
                    "extract_images": extract_images,
                    "save_html": save_html,
                    "debug": debug
                }
            )
        
        # Prepare output path
        output_path = prepare_output_path(config)
        
        # Run the search
        asyncio.run(run_search(config, output_path))
        
    except KeyboardInterrupt:
        logging.info("Search interrupted by user")
        raise typer.Exit(code=130)
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
```

### 3. Update `answer_orchestrator.py`

```python
# Remove the duplicate command definition
# Keep only one @app.command("generate-answer") block

# Update the orchestrate_answer_generation function to accept a configuration object
async def orchestrate_answer_generation(
    query: str, 
    max_urls_to_extract: int = 3,
    config: Optional[Configuration] = None
) -> Dict[str, Any]:
    """
    Orchestrates the end-to-end process of generating an answer to a query.
    
    Args:
        query: The user's query
        max_urls_to_extract: Maximum number of URLs to extract content from
        config: Optional configuration object
        
    Returns:
        Dictionary containing the synthesized answer, source URLs, and metadata
    """
    # Use configuration if provided
    if config:
        max_urls_to_extract = config.search.max_urls
    
    # Rest of the function remains the same
    # ...
```

### 4. Update Search Modules

For each search module (e.g., `selenium_search.py`, `playwright_search.py`, etc.), update the search function to accept configuration parameters:

```python
async def search(
    query: str,
    max_results: int = 10,
    timeout: int = 30,
    proxy: Optional[str] = None,
    user_agent: Optional[str] = None,
    config: Optional[Configuration] = None
) -> List[SearchResult]:
    """
    Perform a search using Selenium.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        timeout: Timeout for search operations in seconds
        proxy: Optional proxy URL
        user_agent: Optional user agent string
        config: Optional configuration object
        
    Returns:
        List of SearchResult objects
    """
    # Use configuration if provided
    if config:
        max_results = config.search.max_results
        timeout = config.search.timeout
        proxy = config.advanced.proxy
        user_agent = config.advanced.user_agent
    
    # Rest of the function remains the same
    # ...
```

### 5. Update `orchestrator.py`

```python
async def run_orchestration(
    query: str,
    modules: Optional[List[str]] = None,
    config: Optional[Configuration] = None
) -> List[SearchResult]:
    """
    Run the search orchestration process.
    
    Args:
        query: The search query
        modules: List of search module names to use (default: all enabled modules)
        config: Optional configuration object
        
    Returns:
        List of SearchResult objects
    """
    # Use configuration if provided
    if config and not modules:
        if config.search.provider != "all":
            modules = config.search.provider.split(",")
    
    # Rest of the function remains the same
    # ...
```

## Testing Plan

### Unit Tests

1. **Configuration Tests**
   - Test loading configuration from environment variables
   - Test loading configuration from YAML file
   - Test merging configuration from different sources
   - Test validation of configuration values

2. **CLI Argument Tests**
   - Test parsing of command-line arguments
   - Test handling of invalid arguments
   - Test default values for arguments

3. **Module Tests**
   - Test search modules with different configuration parameters
   - Test content extraction with different options
   - Test answer synthesis with different LLM configurations

### Integration Tests

1. **End-to-End CLI Tests**
   - Test basic search functionality
   - Test with different search providers
   - Test with different output configurations
   - Test with configuration file

2. **Error Handling Tests**
   - Test handling of network errors
   - Test handling of invalid configurations
   - Test handling of API errors

### Manual Testing

1. **Usability Testing**
   - Test the CLI with different combinations of arguments
   - Verify that output files are created correctly
   - Check that error messages are clear and helpful

2. **Performance Testing**
   - Test with different timeout values
   - Test with different numbers of search results
   - Test with different LLM models

## Documentation Updates

### README.md Updates

Add a section on CLI usage:

```markdown
## Command-Line Interface

The Clinical Metabolomics Oracle Web Search Agent provides a comprehensive command-line interface:

```bash
# Basic usage
python websearch_agent.py search --query "What is clinical metabolomics?"

# Using a specific search provider
python websearch_agent.py search --query "What is clinical metabolomics?" --search-provider "selenium"

# Using a specific LLM model
python websearch_agent.py search --query "What is clinical metabolomics?" --llm-model "gpt-4"

# Saving to a specific output path
python websearch_agent.py search --query "What is clinical metabolomics?" --output-path "./results/metabolomics_answer.json"

# Using a configuration file
python websearch_agent.py search --query "What is clinical metabolomics?" --config-file "./config/default_config.yaml"
```

For full documentation of all available options, run:

```bash
python websearch_agent.py search --help
```
```

### Configuration File Template

Create a template configuration file `config/default_config.yaml`:

```yaml
# Search configuration
search:
  provider: "all"
  max_results: 10
  max_urls: 3
  timeout: 30
  cache: true
  force_refresh: false

# LLM configuration
llm:
  provider: "openrouter"
  model: "gpt-4o-mini"
  temperature: 0.1
  max_tokens: 1024
  evaluation: true

# Output configuration
output:
  directory: "./output"
  file: "answer_result"
  project_name: "default_project"
  
# Advanced options
advanced:
  proxy: null
  user_agent: null
  retry_count: 3
  extract_images: false
  save_html: false
  debug: false
```

## Future Extensions

### 1. Additional Output Formats
- Add support for Markdown output
- Add support for HTML output
- Add support for CSV output for batch processing

### 2. Batch Processing
- Add support for processing multiple queries from a file
- Implement parallel processing of queries

### 3. Interactive Mode
- Add an interactive mode for the CLI
- Implement a REPL (Read-Eval-Print Loop) interface

### 4. Web Interface
- Create a simple web interface for the search agent
- Implement a REST API for the search agent

### 5. Plugin System
- Implement a plugin system for search modules
- Allow for custom search modules to be added

### 6. Caching System
- Implement a more sophisticated caching system
- Add support for different cache backends (Redis, SQLite, etc.)

### 7. Authentication
- Add support for authentication with search APIs
- Implement API key management

### 8. Monitoring and Metrics
- Add support for collecting usage metrics
- Implement monitoring of search performance

### 9. Containerization
- Create a Docker container for the search agent
- Implement Docker Compose for easy deployment

### 10. CI/CD Pipeline
- Set up continuous integration and deployment
- Implement automated testing and deployment
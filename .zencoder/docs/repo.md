# Modular Web Search Agent Information

## Summary
A sophisticated, modular, and extensible web search agent system that aggregates search results from multiple sources including browser automation, commercial APIs, and specialized scraping libraries. The system provides concurrent execution, intelligent result merging, quality evaluation, and comprehensive performance analytics.

## Structure
- **search_agent/**: Main package containing all core functionality
  - **core/**: Core data models and exceptions
  - **modules/**: Search modules (Selenium, Playwright, APIs, etc.)
  - **utils/**: Utility functions and helpers
- **tests/**: Unit tests for the application
- **docs/**: Documentation files

## Language & Runtime
**Language**: Python
**Version**: >=3.9,<3.13
**Build System**: Poetry
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- pydantic (>=2.11.7): Data validation and settings management
- selenium (>=4.34.0): Browser automation
- playwright (>=1.53.0): Modern browser automation
- typer (>=0.16.0): CLI interface
- openai (>=1.0.0): LLM integration
- spacy (>=3.7.0): NLP processing
- beautifulsoup4 (>=4.12.0): HTML parsing
- scrapy (>=2.11.0): Web scraping framework

**Development Dependencies**:
- pytest (^8.4.1): Testing framework
- pytest-mock (^3.14.1): Mocking for tests
- pytest-asyncio (^1.0.0): Async testing support

## Build & Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package
pip install -e .

# Install browser dependencies
playwright install

# Install NLP model
python -m spacy download en_core_web_md
```

## Main Components

### Search Modules
The system includes 6 search modules:
1. **selenium_search**: Traditional browser automation (synchronous)
2. **playwright_search**: Modern browser automation (asynchronous)
3. **brave_api_search**: Brave Search API (asynchronous)
4. **google_cse_search**: Google Custom Search API (asynchronous)
5. **httpx_search**: Lightweight HTTP scraping with BeautifulSoup (asynchronous)
6. **scrapy_search**: Framework-based scraping (asynchronous)

### Orchestration System
The orchestrator (`orchestrator.py`) manages concurrent execution of search modules:
- Dynamically discovers and loads available modules
- Runs modules concurrently using asyncio
- Merges and deduplicates results from all sources
- Re-ranks results using intelligent algorithms

### Answer Generation
The answer orchestrator (`answer_orchestrator.py`) generates synthesized answers:
- Retrieves search results using the search orchestrator
- Extracts content from top search results
- Synthesizes answers using LLM integration
- Evaluates answer quality using multiple metrics

## Data Models
Core data models defined in `core/models.py`:
- **SearchResult**: Individual search result with title, URL, and snippet
- **SearchModuleOutput**: Standardized output from search modules
- **SynthesizedAnswer**: Generated answer with sources and metadata
- **AnswerEvaluationResult**: Quality metrics for generated answers

## Testing
**Framework**: pytest with pytest-asyncio
**Test Location**: tests/ directory
**Naming Convention**: test_*.py
**Run Command**:
```bash
python -m pytest
```

The tests use mocking extensively to test browser automation and API interactions without requiring actual web access.
# Modular Web Search Agent System

A sophisticated, modular, and extensible web search agent system that aggregates search results from multiple sources including browser automation, commercial APIs, and specialized scraping libraries. The system provides concurrent execution, intelligent result merging, quality evaluation, and comprehensive performance analytics.

## 🚀 Features

### Core Capabilities
- **6 Search Modules**: Browser automation (Selenium, Playwright), APIs (Brave, Google), and specialized libraries (httpx, Scrapy)
- **Concurrent Execution**: Run multiple search modules simultaneously for faster results
- **Intelligent Merging**: De-duplicate and merge results from all sources
- **Quality Evaluation**: LLM-based and NLP-based relevance scoring
- **Performance Analytics**: High-precision speed measurement and logging
- **Pluggable Architecture**: Easy to add new modules and evaluation methods

### Search Modules
1. **selenium_search** - Traditional browser automation (sync)
2. **playwright_search** - Modern browser automation (async)
3. **brave_api_search** - Brave Search API (async)
4. **google_cse_search** - Google Custom Search API (async)
5. **httpx_search** - Lightweight HTTP scraping with BeautifulSoup (async)
6. **scrapy_search** - Framework-based scraping (async)

## 📋 Prerequisites

- Python 3.9 or higher
- Virtual environment (recommended)

### API Keys (Optional)
For API-based modules, you'll need:
- **Brave Search API**: Get your key from [Brave Search API](https://brave.com/search/api/)
- **Google Custom Search**: Get API key and CSE ID from [Google Developers Console](https://developers.google.com/custom-search)
- **LLM API Access** (choose one):
  - **OpenRouter API** (recommended): Get your key from [OpenRouter](https://openrouter.ai/)
  - **OpenAI API**: For direct access from [OpenAI](https://platform.openai.com/)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd websearch_agent
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -e .
```

### 4. Install Browser Dependencies
```bash
# For Playwright
playwright install

# For spaCy NLP model
python -m spacy download en_core_web_md
```

### 5. Configure Environment Variables (Optional)
Create a `.env` file in the project root:
```bash
# Search API Keys (optional - modules will be skipped if not provided)
BRAVE_API_KEY=your_brave_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_cse_id_here

# LLM API Keys - You can use either OpenAI directly or OpenRouter
# If both are provided, OpenRouter will be used by default

# OpenAI API Key (direct usage)
# OPENAI_API_KEY=your_openai_api_key_here

# OpenRouter API Key (recommended)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Database Configuration
EVALUATION_DB_PATH=evaluation_log.db

# LLM Configuration
LLM_EVALUATOR_MODEL=gpt-4o-mini
LLM_SYNTHESIZER_MODEL=gpt-4o-mini

# Set to false to use OpenAI directly instead of OpenRouter
USE_OPENROUTER=true

# OpenRouter Configuration
OPENROUTER_REFERER=https://websearch-agent.example.com
```

## 🚀 Quick Start

### Basic Search with Orchestrator
```bash
# Run search across all available modules
python -m search_agent.orchestrator search "python programming"

# Save results to file
python -m search_agent.orchestrator search "machine learning" --output results.json

# List all available modules
python -m search_agent.orchestrator list-modules
```

### Individual Module Usage
```bash
# Selenium (browser automation)
python -m search_agent.modules.selenium_search --query "web scraping"

# Playwright (modern browser automation)
python -m search_agent.modules.playwright_search --query "async programming"

# Brave API (requires API key)
python -m search_agent.modules.brave_api_search --query "search engines"

# Google CSE (requires API key and CSE ID)
python -m search_agent.modules.google_cse_search --query "custom search"

# httpx + BeautifulSoup (lightweight scraping)
python -m search_agent.modules.httpx_search --query "web development"

# Scrapy (framework-based scraping)
python -m search_agent.modules.scrapy_search --query "data extraction"
```

### Performance Evaluation
```bash
# Initialize evaluation database
python -m search_agent.evaluator init-db

# Measure module speed
python -m search_agent.evaluator evaluate-speed selenium_search "test query"
python -m search_agent.evaluator evaluate-speed playwright_search "test query"
```

## 📖 Usage Examples

### Python Library Usage
```python
import asyncio
from search_agent.orchestrator import run_orchestration
from search_agent.modules.selenium_search import search as selenium_search
from search_agent.evaluator import evaluate_quality_nlp, evaluate_quality_llm

# Use orchestrator for concurrent search
async def main():
    result = await run_orchestration("python programming")
    print(f"Found {len(result.results)} unique results")
    print(f"Total execution time: {result.execution_time_seconds:.2f}s")

# Use individual module
result = selenium_search("web scraping")
print(result.model_dump_json(indent=2))

# Evaluate result quality
nlp_score = evaluate_quality_nlp(result)
print(f"NLP similarity score: {nlp_score:.3f}")

# LLM evaluation (requires OpenAI API key)
llm_score = evaluate_quality_llm(result)
print(f"LLM quality score: {llm_score}/10")
```

### Advanced Configuration
```python
from search_agent.config import settings

# Check current configuration
print(f"Database path: {settings.EVALUATION_DB_PATH}")
print(f"LLM model: {settings.LLM_EVALUATOR_MODEL}")
print(f"Brave API configured: {bool(settings.BRAVE_API_KEY)}")
```

## 🏗️ Architecture

### Project Structure
```
websearch_agent/
├── search_agent/
│   ├── core/
│   │   ├── models.py          # Pydantic data models
│   │   └── exceptions.py      # Custom exceptions
│   ├── modules/
│   │   ├── selenium_search.py    # Browser automation
│   │   ├── playwright_search.py  # Modern browser automation
│   │   ├── brave_api_search.py   # Brave Search API
│   │   ├── google_cse_search.py  # Google Custom Search
│   │   ├── httpx_search.py       # Lightweight scraping
│   │   └── scrapy_search.py      # Framework scraping
│   ├── orchestrator.py        # Central coordination
│   ├── evaluator.py          # Performance evaluation
│   └── config.py             # Configuration management
├── tests/                    # Unit tests
├── docs/                     # Documentation
└── pyproject.toml           # Project configuration
```

### Data Flow
1. **Query Input** → Orchestrator receives search query
2. **Module Discovery** → Dynamically imports available search modules
3. **Concurrent Execution** → Runs modules in parallel using asyncio
4. **Result Collection** → Gathers results from all successful modules
5. **Merging & Deduplication** → Combines and removes duplicate results
6. **Re-ranking** → Applies intelligent ranking algorithms
7. **Output** → Returns standardized JSON response

### Key Components

#### SearchResult Model
```python
class SearchResult(BaseModel):
    title: str          # Result title
    url: HttpUrl        # Result URL
    snippet: str        # Description/snippet
```

#### SearchModuleOutput Model
```python
class SearchModuleOutput(BaseModel):
    source_name: str                    # Module identifier
    query: str                         # Original query
    timestamp_utc: datetime            # Execution timestamp
    execution_time_seconds: float      # Performance metric
    results: List[SearchResult]        # Search results
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BRAVE_API_KEY` | Brave Search API key | No | None |
| `GOOGLE_API_KEY` | Google API key | No | None |
| `GOOGLE_CSE_ID` | Google Custom Search Engine ID | No | None |
| `OPENROUTER_API_KEY` | OpenRouter API key (recommended) | No* | None |
| `OPENAI_API_KEY` | OpenAI API key (alternative to OpenRouter) | No* | None |
| `USE_OPENROUTER` | Whether to use OpenRouter instead of OpenAI directly | No | `true` |
| `OPENROUTER_BASE_URL` | OpenRouter API base URL | No | `https://openrouter.ai/api/v1` |
| `OPENROUTER_REFERER` | HTTP referer for OpenRouter API | No | `https://websearch-agent.example.com` |
| `EVALUATION_DB_PATH` | SQLite database path | No | `evaluation_log.db` |
| `LLM_EVALUATOR_MODEL` | LLM model for evaluation | No | `gpt-4o-mini` |
| `LLM_SYNTHESIZER_MODEL` | LLM model for answer synthesis | No | `gpt-4o-mini` |

\* Either `OPENROUTER_API_KEY` or `OPENAI_API_KEY` is required for LLM-based features

### Module Configuration
Each module can be configured independently:

- **Browser modules** (Selenium, Playwright): Headless mode, user agents, timeouts
- **API modules** (Brave, Google): Rate limiting, result counts, safety filters
- **Scraping modules** (httpx, Scrapy): Request headers, delays, concurrent requests

## 📊 Performance & Evaluation

### Speed Evaluation
The system measures execution time with high precision using `time.perf_counter()`:
```bash
python -m search_agent.evaluator evaluate-speed selenium_search "test query"
```

### Quality Evaluation

#### NLP-based Similarity
Uses spaCy word vectors to calculate cosine similarity between query and results:
```python
from search_agent.evaluator import evaluate_quality_nlp
score = evaluate_quality_nlp(search_output)  # Returns 0.0-1.0
```

#### LLM-based Relevance
Uses OpenAI GPT models to provide human-like quality assessment:
```python
from search_agent.evaluator import evaluate_quality_llm
score = evaluate_quality_llm(search_output)  # Returns 1-10
```

### Database Logging
All evaluation metrics are stored in SQLite for analysis:
```sql
-- Evaluation log schema
CREATE TABLE evaluation_log (
    id INTEGER PRIMARY KEY,
    run_timestamp_utc TEXT,
    module_name TEXT,
    query TEXT,
    execution_time_seconds REAL,
    llm_quality_score INTEGER,
    nlp_similarity_score REAL,
    result_count INTEGER,
    was_successful INTEGER,
    error_message TEXT,
    raw_output_json TEXT
);
```

## 🧪 Testing

### Run Unit Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_selenium_search.py -v

# Run with coverage
python -m pytest --cov=search_agent
```

### Test Individual Modules
```bash
# Test each module independently
python -m search_agent.modules.selenium_search --query "test"
python -m search_agent.modules.playwright_search --query "test"
python -m search_agent.modules.httpx_search --query "test"
```

## 🔍 Troubleshooting

### Common Issues

#### Browser Driver Issues
```bash
# Update Chrome driver
python -m webdriver_manager.chrome

# Reinstall Playwright browsers
playwright install --force
```

#### Missing Dependencies
```bash
# Reinstall all dependencies
pip install -e . --force-reinstall

# Install specific components
python -m spacy download en_core_web_md
```

#### API Configuration
```bash
# Check API key configuration
python -c "from search_agent.config import settings; print(f'Brave: {bool(settings.BRAVE_API_KEY)}')"
```

#### Module Import Errors
```bash
# Test module imports
python -c "from search_agent.modules import selenium_search; print('OK')"
```

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Advanced Usage

### Custom Module Development
Create new search modules by following the standard interface:

```python
# search_agent/modules/custom_search.py
import asyncio
import time
from datetime import datetime, timezone
import typer
from search_agent.core.models import SearchResult, SearchModuleOutput

app = typer.Typer()

async def search(query: str) -> SearchModuleOutput:
    start_time = time.perf_counter()
    
    # Your custom search logic here
    results = []  # List of SearchResult objects
    
    end_time = time.perf_counter()
    
    return SearchModuleOutput(
        source_name="custom_search",
        query=query,
        timestamp_utc=datetime.now(timezone.utc),
        execution_time_seconds=end_time - start_time,
        results=results
    )

@app.command()
def main(query: str = typer.Option(..., "--query", "-q")):
    result = asyncio.run(search(query))
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    app()
```

### Custom Re-ranking Algorithms
Extend the orchestrator with custom ranking:

```python
def custom_rerank_results(results: List[SearchResult]) -> List[SearchResult]:
    # Your custom ranking logic
    return sorted(results, key=lambda r: len(r.title))
```

### Batch Processing
Process multiple queries:

```python
import asyncio
from search_agent.orchestrator import run_orchestration

async def batch_search(queries: List[str]):
    tasks = [run_orchestration(query) for query in queries]
    results = await asyncio.gather(*tasks)
    return results

# Usage
queries = ["python", "javascript", "machine learning"]
results = asyncio.run(batch_search(queries))
```

## 📈 Performance Optimization

### Concurrent Execution
The orchestrator automatically runs modules concurrently:
- Async modules run natively
- Sync modules wrapped with `asyncio.to_thread()`
- Exception handling prevents single module failures from affecting others

### Caching (Future Enhancement)
Consider implementing result caching:
```python
# Potential caching layer
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str, module: str):
    # Cache results for repeated queries
    pass
```

### Resource Management
- Browser instances are properly closed
- HTTP connections use connection pooling
- Database connections use context managers

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup development environment
git clone <repository-url>
cd websearch_agent
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints throughout
- Add docstrings to all public functions
- Write unit tests for new features

### Adding New Modules
1. Create module file in `search_agent/modules/`
2. Implement standard interface (async `search()` function)
3. Add Typer CLI wrapper
4. Write unit tests
5. Update orchestrator module list
6. Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with modern Python async/await patterns
- Uses industry-standard libraries (Selenium, Playwright, Scrapy)
- Follows clean architecture principles
- Implements comprehensive error handling and logging

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review existing issues in the repository
3. Create a new issue with detailed information
4. Include error messages and system information

---

**Happy Searching! 🔍✨**
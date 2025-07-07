# Clinical Metabolomics Oracle Web Search Agent Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Reference](#api-reference)
7. [Output Files](#output-files)
8. [Integration Guide](#integration-guide)
9. [Development Roadmap](#development-roadmap)
10. [Troubleshooting](#troubleshooting)
11. [Performance Metrics](#performance-metrics)

## Introduction

The Clinical Metabolomics Oracle Web Search Agent is a sophisticated system designed to search the web for information, extract relevant content, and generate comprehensive answers to user queries. The system leverages multiple search modules, content extraction techniques, and large language models (LLMs) to provide accurate and informative responses.

### Key Features
- Multi-module web search capabilities (Selenium, Playwright, Brave API, Google CSE)
- Intelligent content extraction from web pages
- Answer synthesis using LLMs via OpenRouter or OpenAI
- Answer quality evaluation with multiple metrics
- Comprehensive logging and error handling
- Modular and extensible architecture
- **Flexible provider selection:** You can run any subset of search modules (e.g., only Selenium) via CLI or configuration. The orchestrator will skip unavailable or misconfigured modules and continue with available ones.

## System Architecture

The system follows a modular architecture with several key components:

### Core Components
1. **Search Orchestrator**: Coordinates multiple search modules and aggregates results
2. **Answer Orchestrator**: Manages the end-to-end process from search to answer generation
3. **Web Content Extractor**: Extracts relevant content from web pages
4. **Answer Synthesizer**: Generates answers using LLMs based on extracted content
5. **Answer Evaluator**: Evaluates the quality of generated answers

### Search Modules
1. **Selenium Search**: Uses Selenium WebDriver to search DuckDuckGo
2. **Playwright Search**: Uses Playwright to search DuckDuckGo
3. **Brave API Search**: Uses the Brave Search API
4. **Google CSE Search**: Uses Google Custom Search Engine

**Provider selection:** You can specify which search provider(s) to use with the `--search-provider` CLI argument or in your configuration file. If a provider is missing required configuration (e.g., API keys), it will be skipped and errors will be logged.

### Data Flow
1. User query is sent to the Answer Orchestrator
2. Answer Orchestrator passes the query to the Search Orchestrator
3. Search Orchestrator runs multiple search modules concurrently
4. Search results are merged, deduplicated, and ranked
5. Top URLs are selected for content extraction
6. Web Content Extractor fetches and processes content from selected URLs
7. Answer Synthesizer generates an answer using the extracted content
8. Answer Evaluator assesses the quality of the generated answer
9. Final result is returned to the user

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)
- Chrome browser (for Selenium and Playwright modules)
- Git (for cloning the repository)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Clinical_Metabolomics_Oracle.git
   cd Clinical_Metabolomics_Oracle/websearch_agent
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Using venv
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install browser drivers for Selenium and Playwright**
   ```bash
   # Install Playwright browsers
   playwright install
   
   # WebDriver Manager will handle Selenium drivers automatically
   ```

5. **Set up environment variables**
   Create a `.env` file in the project root with the following variables:
   ```
   # LLM API Configuration
   USE_OPENROUTER=True
   OPENROUTER_API_KEY=your_openrouter_api_key
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_REFERER=https://yourdomain.com
   
   # Fallback to direct OpenAI (if OpenRouter is not used)
   OPENAI_API_KEY=your_openai_api_key
   
   # Search API Keys (optional)
   BRAVE_API_KEY=your_brave_api_key
   GOOGLE_CSE_API_KEY=your_google_cse_api_key
   GOOGLE_CSE_ID=your_google_cse_id
   
   # Search Configuration
   MAX_SEARCH_RESULTS=10
   MAX_URLS_TO_EXTRACT=3
   
   # LLM Configuration
   DEFAULT_LLM_MODEL=gpt-4o-mini
   LLM_TEMPERATURE=0.1
   LLM_MAX_TOKENS=1024
   ```

6. **Verify installation**
   ```bash
   python -c "import search_agent; print('Installation successful!')"
   ```

## Configuration

### Environment Variables
The system uses environment variables for configuration, which can be set in a `.env` file or directly in the environment.

| Variable | Description | Default |
|----------|-------------|---------|
| `USE_OPENROUTER` | Whether to use OpenRouter for LLM API calls | `True` |
| `OPENROUTER_API_KEY` | API key for OpenRouter | None |
| `OPENROUTER_BASE_URL` | Base URL for OpenRouter API | `https://openrouter.ai/api/v1` |
| `OPENROUTER_REFERER` | Referer header for OpenRouter API | None |
| `OPENAI_API_KEY` | API key for OpenAI (fallback) | None |
| `BRAVE_API_KEY` | API key for Brave Search | None |
| `GOOGLE_CSE_API_KEY` | API key for Google Custom Search Engine | None |
| `GOOGLE_CSE_ID` | ID for Google Custom Search Engine | None |
| `MAX_SEARCH_RESULTS` | Maximum number of search results to retrieve | `10` |
| `MAX_URLS_TO_EXTRACT` | Maximum number of URLs to extract content from | `3` |
| `DEFAULT_LLM_MODEL` | Default LLM model to use | `gpt-4o-mini` |
| `LLM_TEMPERATURE` | Temperature parameter for LLM | `0.1` |
| `LLM_MAX_TOKENS` | Maximum tokens for LLM response | `1024` |

**Note:** If a search provider is missing required configuration (such as an API key), the orchestrator will skip that provider and continue with the available modules. Errors will be logged but will not stop the answer generation process.

### Advanced Configuration
For advanced configuration, you can modify the following files:
- `search_agent/config.py`: Core configuration settings
- `search_agent/orchestrator.py`: Search orchestration parameters
- `search_agent/answer_orchestrator.py`: Answer generation parameters
- `search_agent/modules/web_content_extractor.py`: Content extraction settings

## Usage

### Command Line Interface
The system includes a test script that demonstrates the basic functionality:

```bash
python test_answer_generation.py
```

You can modify the query in the script to test different questions.

**To run with a specific search provider (e.g., Selenium only):**
```bash
python websearch_agent.py search "What is today's day?" --search-provider selenium --llm-provider openrouter --llm-model openrouter/cypher-alpha:free
```

You can also specify multiple providers as a comma-separated list (e.g., `--search-provider selenium,playwright`).

### Python API
To use the system in your Python code:

```python
import asyncio
from search_agent.answer_orchestrator import orchestrate_answer_generation

async def get_answer(query):
    result = await orchestrate_answer_generation(query)
    return result

# Run the async function
query = "What is clinical metabolomics?"
result = asyncio.run(get_answer(query))
print(result["synthesized_answer"]["answer"])
```

### Web API
To deploy the system as a web API, you can use the included FastAPI application:

```bash
uvicorn api.main:app --reload
```

Then you can make requests to the API:
```bash
curl -X POST "http://localhost:8000/api/answer" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is clinical metabolomics?"}'
```

## API Reference

### `orchestrate_answer_generation(query: str) -> Dict[str, Any]`
The main function for generating answers to queries.

**Parameters:**
- `query` (str): The user's query

**Returns:**
- Dictionary containing:
  - `query`: The original query
  - `synthesized_answer`: Dictionary with the answer, source URLs, and timestamp
  - `evaluation_results`: Dictionary with quality metrics
  - `source_urls`: List of URLs used as sources
  - `extracted_contents`: List of extracted content from each URL
  - `timestamp_utc`: UTC timestamp
  - `execution_time_seconds`: Total execution time
  - `metadata`: Additional metadata about the process

### `search_orchestrator.orchestrate_search(query: str) -> List[SearchResult]`
Orchestrates the search process across multiple search modules.

**Parameters:**
- `query` (str): The search query

**Returns:**
- List of `SearchResult` objects

### `web_content_extractor.extract_content(url: str) -> str`
Extracts content from a web page.

**Parameters:**
- `url` (str): The URL to extract content from

**Returns:**
- Extracted content as a string

### `answer_synthesizer.synthesize_answer(query: str, content_snippets: List[str]) -> str`
Synthesizes an answer using an LLM.

**Parameters:**
- `query` (str): The user's query
- `content_snippets` (List[str]): List of content snippets to use for answer generation

**Returns:**
- Synthesized answer as a string

### `answer_evaluator.evaluate_answer_quality(query: str, synthesized_answer: str, original_content: List[str]) -> Dict[str, Any]`
Evaluates the quality of a synthesized answer.

**Parameters:**
- `query` (str): The user's query
- `synthesized_answer` (str): The synthesized answer
- `original_content` (List[str]): The original content used to generate the answer

**Returns:**
- Dictionary with quality metrics

### Orchestrator Robustness
- The orchestrator is robust to search modules with or without a `config` parameter. It will call each module appropriately based on its function signature.
- If a search module fails (e.g., due to missing configuration or runtime error), the error is logged and the orchestrator continues with the remaining modules.

## Output Files

The system generates the following output files:

### `answer_generation_result.json`
Contains the complete result of the answer generation process, including:
- The original query
- The synthesized answer
- Source URLs
- Extracted content
- Evaluation results
- Metadata

Example location: `/Users/Mark/Research/Clinical_Metabolomics_Oracle/websearch_agent/answer_generation_result.json`

### Log Files
The system logs information to the console and can be configured to log to files as well. Log messages include:
- Search process details
- Content extraction results
- Answer synthesis and evaluation
- Errors and warnings

## Integration Guide

### Importing as a Module
To import the system as a module in another script:

```python
# Import the main orchestration function
from search_agent.answer_orchestrator import orchestrate_answer_generation

# Import specific components if needed
from search_agent.orchestrator import orchestrate_search
from search_agent.modules.web_content_extractor import extract_content
from search_agent.answer_synthesizer import synthesize_answer
from search_agent.answer_evaluator import evaluate_answer_quality

# Import models
from search_agent.core.models import SearchResult, AnswerResult
```

### Integration with Web Applications
To integrate with a web application:

1. **FastAPI Example**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

from search_agent.answer_orchestrator import orchestrate_answer_generation

app = FastAPI()

class Query(BaseModel):
    query: str

class Answer(BaseModel):
    answer: str
    sources: list[str]

@app.post("/api/answer", response_model=Answer)
async def get_answer(query: Query):
    try:
        result = await orchestrate_answer_generation(query.query)
        return {
            "answer": result["synthesized_answer"]["answer"],
            "sources": result["source_urls"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

2. **Flask Example**
```python
from flask import Flask, request, jsonify
import asyncio

from search_agent.answer_orchestrator import orchestrate_answer_generation

app = Flask(__name__)

@app.route("/api/answer", methods=["POST"])
def get_answer():
    query = request.json.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        result = asyncio.run(orchestrate_answer_generation(query))
        return jsonify({
            "answer": result["synthesized_answer"]["answer"],
            "sources": result["source_urls"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Integration with Desktop Applications
For desktop applications, you can use the async API directly:

```python
import asyncio
import tkinter as tk
from tkinter import scrolledtext

from search_agent.answer_orchestrator import orchestrate_answer_generation

class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Search Agent")
        
        self.query_label = tk.Label(root, text="Query:")
        self.query_label.pack()
        
        self.query_entry = tk.Entry(root, width=50)
        self.query_entry.pack()
        
        self.search_button = tk.Button(root, text="Search", command=self.search)
        self.search_button.pack()
        
        self.result_text = scrolledtext.ScrolledText(root, width=80, height=20)
        self.result_text.pack()
    
    def search(self):
        query = self.query_entry.get()
        if not query:
            return
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Searching...\n")
        
        # Run the search in a separate thread to avoid blocking the UI
        import threading
        threading.Thread(target=self.run_search, args=(query,)).start()
    
    def run_search(self, query):
        result = asyncio.run(orchestrate_answer_generation(query))
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Answer:\n{result['synthesized_answer']['answer']}\n\n")
        self.result_text.insert(tk.END, "Sources:\n")
        for url in result["source_urls"]:
            self.result_text.insert(tk.END, f"- {url}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchApp(root)
    root.mainloop()
```

## Development Roadmap

### Short-Term Improvements
1. **Fix Google CSE Search Module**: Resolve the issue with the `SearchResponse` import in the Google CSE search module.
2. **Improve Content Extraction**: Enhance the content extraction module to handle more website formats and overcome SSL certificate issues.
3. **Add Retry Mechanism**: Implement a retry mechanism for failed content extraction attempts.
4. **Optimize Search Ranking**: Improve the ranking algorithm for search results to prioritize more relevant sources.
5. **Enhance Error Handling**: Add more robust error handling and recovery mechanisms.

### Medium-Term Goals
1. **Add More Search Modules**: Integrate additional search engines and APIs (Bing, Qwant, etc.).
2. **Implement Caching**: Add a caching layer to store search results and extracted content for faster responses.
3. **Improve Answer Synthesis**: Enhance the answer synthesis process with better prompting techniques and model selection.
4. **Add Support for Images**: Extend the system to handle image-based queries and include images in answers.
5. **Implement User Feedback Loop**: Add a mechanism to collect user feedback on answer quality and use it to improve the system.

### Long-Term Vision
1. **Multi-Modal Support**: Extend the system to handle various types of queries (text, images, audio).
2. **Domain-Specific Knowledge**: Add support for domain-specific knowledge bases and specialized search.
3. **Continuous Learning**: Implement a continuous learning mechanism to improve the system over time.
4. **Distributed Architecture**: Scale the system to handle high volumes of queries with a distributed architecture.
5. **Integration with Knowledge Graphs**: Connect the system to knowledge graphs for more structured information retrieval.

## Troubleshooting

### Common Issues and Solutions

#### SSL Certificate Errors
**Issue**: `[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate`

**Solution**:
1. Update your CA certificates:
   ```bash
   pip install --upgrade certifi
   ```
2. Set the SSL verification environment variable:
   ```bash
   export PYTHONHTTPSVERIFY=0
   ```
3. Modify the code to bypass SSL verification (not recommended for production):
   ```python
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

#### HTTP 403 Forbidden Errors
**Issue**: `HTTP error 403 while fetching URL: Client error '403 Forbidden'`

**Solution**:
1. Add user-agent headers to requests:
   ```python
   headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
   }
   ```
2. Implement rate limiting to avoid being blocked by websites.
3. Use a proxy rotation service for high-volume requests.

#### Playwright Timeout Errors
**Issue**: `Playwright timeout error: Page.wait_for_selector: Timeout 30000ms exceeded.`

**Solution**:
1. Increase the timeout value:
   ```python
   page.wait_for_selector("[data-testid='result']", timeout=60000)
   ```
2. Use more robust selectors that are less likely to change.
3. Implement a fallback mechanism to handle timeout errors.

#### LLM API Errors
**Issue**: `No valid API key found. Please set either OPENROUTER_API_KEY or OPENAI_API_KEY in your .env file.`

**Solution**:
1. Ensure that the API keys are correctly set in the `.env` file.
2. Check that the `.env` file is in the correct location.
3. Verify that the API keys are valid and have not expired.

### Debugging Tips
1. **Enable Verbose Logging**: Set the logging level to DEBUG for more detailed information:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Inspect Network Requests**: Use a tool like mitmproxy to inspect network requests:
   ```bash
   mitmproxy -p 8080
   ```
   Then set the HTTP_PROXY and HTTPS_PROXY environment variables:
   ```bash
   export HTTP_PROXY=http://localhost:8080
   export HTTPS_PROXY=http://localhost:8080
   ```

3. **Step-by-Step Execution**: Run each component separately to identify the source of issues:
   ```python
   # Run just the search
   search_results = await orchestrate_search(query)
   
   # Extract content from a specific URL
   content = await extract_content(url)
   
   # Synthesize an answer with specific content
   answer = await synthesize_answer(query, [content])
   ```

### Error Handling Notes
- If a search provider fails (e.g., due to missing API keys, timeouts, or other errors), the orchestrator logs the error and continues with the available results. This ensures that answer generation is robust and not blocked by individual module failures.

## Performance Metrics

Based on our testing, here are the performance metrics for the system:

### Query: "What is clinical metabolomics?"
- **Search Time**: 31.90 seconds
- **Content Extraction Time**: 0.89 seconds
- **Answer Synthesis Time**: 1.65 seconds
- **Answer Evaluation Time**: 3.70 seconds
- **Total Execution Time**: 38.13 seconds
- **URLs Found**: 10
- **URLs Selected**: 3
- **Extraction Success**: 1
- **Extraction Failures**: 2

### Query: "What are the main applications of metabolomics in medicine?"
- **Search Time**: 32.03 seconds
- **Content Extraction Time**: 5.01 seconds
- **Answer Synthesis Time**: 5.39 seconds
- **Answer Evaluation Time**: 6.71 seconds
- **Total Execution Time**: 49.16 seconds
- **URLs Found**: 10
- **URLs Selected**: 3
- **Extraction Success**: 3
- **Extraction Failures**: 0

### Performance Optimization Tips
1. **Parallel Processing**: Increase the number of concurrent search and extraction processes.
2. **Caching**: Implement caching for search results and extracted content.
3. **Selective Content Extraction**: Only extract content from the most promising URLs.
4. **Optimized LLM Prompts**: Use more efficient prompts to reduce token usage and processing time.
5. **Hardware Acceleration**: Use GPU acceleration for LLM inference if available.

---

This documentation provides a comprehensive overview of the Clinical Metabolomics Oracle Web Search Agent. For further assistance or to report issues, please contact the development team or open an issue on the GitHub repository.
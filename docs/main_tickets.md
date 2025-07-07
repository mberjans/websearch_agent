### **Phase 1: Foundational Architecture & MVP**

This phase focuses on establishing the project's core structure and delivering the first functional search module.

---

Ticket ID: WSA-101  
Title: Setup Project Structure, Dependency, and Environment Management  
Description:  
Initialize the project with a standardized, modular structure to ensure maintainability and scalability.1 This task involves creating the directory layout and configuring the dependency management tool.

Acceptance Criteria:

1. The project directory structure is created as specified in Section 1.1 of the development plan.  
2. The project is initialized with Poetry for dependency management. Using Poetry over pip is mandated due to its superior dependency resolution and ability to create reproducible environments with a poetry.lock file, preventing "dependency hell".4  
3. A pyproject.toml file is created, defining project metadata and initial dependencies.  
4. A .gitignore file is created to exclude virtual environments, .env files, and other non-source files from version control.

---

Ticket ID: WSA-102  
Title: Implement Core Interfaces and Configuration Management  
Description:  
Develop the core data contracts and configuration system that will be used by all modules. This is critical for ensuring interoperability and secure handling of credentials.  
Acceptance Criteria:

1. Pydantic models for SearchResult and SearchModuleOutput are created in search\_agent/core/models.py to enforce a standardized JSON I/O schema.  
2. A centralized configuration module search\_agent/config.py is created using Pydantic's BaseSettings. This approach provides type-safe, validated settings loaded from environment variables, which is a best practice for security and flexibility.10  
3. An .env.template file is created to document required environment variables. The actual .env file must be included in .gitignore.  
4. Custom exception classes (ScrapingError, NoResultsError, etc.) are defined in search\_agent/core/exceptions.py.

---

Ticket ID: WSA-103  
Title: Implement Selenium Search Module (MVP)  
Description:  
Develop the first search module using Selenium. This module will serve as the proof-of-concept for the dual-mode (CLI/library) architecture and headless browser operation.  
Acceptance Criteria:

1. Create search\_agent/modules/selenium\_search.py.  
2. The module must implement the dual-mode pattern using Typer, providing both an importable search() function and a command-line interface.14  
3. Selenium WebDriver is configured to run Chrome or Firefox in headless mode (--headless=new) for server-side execution.20  
4. The script successfully navigates to DuckDuckGo, submits a query, and scrapes the titles, URLs, and snippets from the first page of results.26  
5. The output is formatted into the standardized JSON structure using the SearchModuleOutput Pydantic model.  
6. The WebDriver instance is properly closed in a finally block to prevent resource leaks.

---

Ticket ID: WSA-104  
Title: Unit Tests for Selenium Search Module  
Description:  
Create a suite of unit tests to validate the functionality of the Selenium search module.  
Acceptance Criteria:

1. A tests/test\_selenium\_search.py file is created.  
2. Tests are written to verify the core logic of the search() function.  
3. Mocking is used to simulate web requests and HTML responses, so tests can run without actual browser interaction.  
4. Tests verify that the module correctly parses sample HTML and produces the expected JSON output.  
5. Tests confirm that custom exceptions are raised under appropriate failure conditions (e.g., page timeout, no results found).

### **Phase 2: Architectural Validation**

This phase proves the modular architecture by adding a second, technologically distinct search module.

---

Ticket ID: WSA-201  
Title: Implement Playwright Search Module  
Description:  
Develop a second search module using Playwright to validate the system's modularity. Playwright is chosen for its modern architecture, native asyncio support, and performance advantages over Selenium.32

Acceptance Criteria:

1. Create search\_agent/modules/playwright\_search.py.  
2. The module must adhere to the exact same dual-mode and standardized JSON I/O interfaces as the Selenium module.  
3. The core search() function must be implemented using Playwright's async API.  
4. The module must operate in headless mode.  
5. The module successfully scrapes search results from the target search engine.

---

Ticket ID: WSA-202  
Title: Unit Tests for Playwright Search Module  
Description:  
Create unit tests for the Playwright search module to ensure its correctness and adherence to the system's interfaces.  
Acceptance Criteria:

1. A tests/test\_playwright\_search.py file is created.  
2. Async-compatible tests are written for the async def search() function.  
3. Tests use mocking to avoid actual browser execution and validate the parsing and JSON output logic against sample HTML.

### **Phase 3: The Quantitative Evaluator Module**

This phase focuses on building the tools to measure and log the performance and quality of all search modules.

---

Ticket ID: WSA-301  
Title: Implement Speed Evaluation Logic  
Description:  
Implement the functionality within evaluator.py to programmatically execute any search module and accurately measure its execution time.  
Acceptance Criteria:

1. An evaluator.py module is created.  
2. A function is implemented that can dynamically import and run the search() function from any given module.  
3. Execution time is measured using time.perf\_counter() for high precision, as it is more suitable for benchmarking than time.time().38  
4. The measured duration is returned for logging.

---

Ticket ID: WSA-302  
Title: Implement LLM-Based Quality Evaluation  
Description:  
Integrate with an LLM API to provide a human-like quality and relevance score for a given set of search results.  
Acceptance Criteria:

1. The evaluator integrates with an LLM client (e.g., OpenAI). API keys are managed via the central config.py module.43  
2. A well-defined prompt is engineered to instruct the LLM to return a single integer score (1-10) based on the relevance of the results to the query. The prompt must be specific to ensure consistent, structured output.48  
3. The function takes a SearchModuleOutput object as input and returns the integer score from the LLM.

---

Ticket ID: WSA-303  
Title: Implement NLP-Based Quality Evaluation  
Description:  
Implement a non-LLM, deterministic quality scoring method using cosine similarity to measure the semantic relevance between the query and the result snippets.  
Acceptance Criteria:

1. The evaluator integrates the spaCy library.  
2. A function is created that takes a query string and a list of result snippets.  
3. The function calculates the cosine similarity between the query's vector and the averaged vector of the result snippets.53  
4. The function returns a similarity score between 0 and 1\.

---

Ticket ID: WSA-304  
Title: Implement SQLite Logging for Evaluation Results  
Description:  
Create a data persistence layer using SQLite to log all evaluation metrics for later analysis. SQLite is chosen for its simplicity and lack of external dependencies.58

Acceptance Criteria:

1. A function is created to initialize an SQLite database (evaluation\_log.db) with the schema defined in Table 1 of the development plan.  
2. A function is implemented to insert a new record into the log table, containing the module name, query, execution time, quality scores, and other metadata.  
3. All database interactions are handled via the sqlite3 module.

### **Phase 4: The Central Orchestrator**

This phase involves building the system's brain, which manages modules and combines their results.

---

Ticket ID: WSA-401  
Title: Implement Concurrent Module Execution  
Description:  
Implement the core logic of the Orchestrator to run multiple search modules concurrently for a single query. asyncio is the chosen technology as the search tasks are I/O-bound.63

Acceptance Criteria:

1. An orchestrator.py module is created.  
2. The orchestrator uses asyncio.gather() to execute multiple search modules in parallel.  
3. Synchronous modules (like Selenium) are wrapped with asyncio.to\_thread() to prevent blocking the event loop.  
4. The orchestrator gracefully handles and logs exceptions from individual modules, allowing the system to return partial results if one module fails.

---

Ticket ID: WSA-402  
Title: Implement Result Merging and De-duplication  
Description:  
Develop an algorithm to combine the result lists from multiple modules into a single, de-duplicated list.  
Acceptance Criteria:

1. A function is created that takes a list of SearchModuleOutput objects.  
2. Results are de-duplicated based on the url field. An efficient approach using a dictionary or a set to track seen URLs should be used to maintain performance.69  
3. The function returns a single, de-duplicated list of SearchResult objects.

---

Ticket ID: WSA-403  
Title: Implement Initial Re-ranking Strategy  
Description:  
Implement a basic, heuristic-based re-ranking algorithm to order the final merged list of results.  
Acceptance Criteria:

1. A re-ranking function is created that takes the de-duplicated list of results.  
2. The initial strategy re-ranks results based on their source (e.g., API-based results are prioritized over scraped results).  
3. The function is designed to be pluggable, allowing for more advanced strategies (like Cross-Encoder or MMR) to be added later.73

### **Phase 5: Integration of API-Based Search Modules**

This phase expands the system's capabilities with fast and reliable commercial search APIs.

---

Ticket ID: WSA-501  
Title: Implement Brave Search API Module  
Description:  
Create a new search module that queries the Brave Search API. This will provide a high-speed, reliable data source.  
Acceptance Criteria:

1. Create search\_agent/modules/brave\_api\_search.py.  
2. The module uses an async HTTP client (like httpx) or the official brave-search Python library to interact with the Brave Search API.79  
3. The module adheres to the standard dual-mode and JSON output format.  
4. The API key is securely retrieved from the central configuration.

---

Ticket ID: WSA-502  
Title: Implement Google Custom Search API Module  
Description:  
Create a new search module that queries the Google Custom Search Engine (CSE) API.  
Acceptance Criteria:

1. Create search\_agent/modules/google\_cse\_search.py.  
2. The module uses the official Google API Python Client to interact with the CSE API.84  
3. The module adheres to the standard dual-mode and JSON output format.  
4. The API Key and Search Engine ID (CX) are securely retrieved from the central configuration.

### **Phase 6: Expansion with Specialized Python Libraries**

This final phase completes the suite of search agents with modules for other powerful libraries.

---

Ticket ID: WSA-601  
Title: Implement httpx \+ BeautifulSoup Search Module  
Description:  
Develop a lightweight, high-speed search module for simple, static HTML search engines. httpx is chosen for its performance and async capabilities, making it ideal for this task.86

Acceptance Criteria:

1. Create search\_agent/modules/httpx\_search.py.  
2. The module uses httpx to fetch HTML content asynchronously.  
3. BeautifulSoup is used to parse the HTML and extract results.  
4. The module adheres to all standard architectural patterns (dual-mode, JSON output).

---

Ticket ID: WSA-602  
Title: Implement Scrapy Search Module  
Description:  
Develop a search module using the Scrapy framework. Scrapy is chosen for its power in handling more complex, large-scale scraping tasks that might involve following links or complex data extraction pipelines.32

Acceptance Criteria:

1. Create search\_agent/modules/scrapy\_search.py.  
2. The module is structured as a self-contained Scrapy project that can be invoked from the main search() function.  
3. The Scrapy spider is configured to perform a search and extract results.  
4. The module adheres to all standard architectural patterns (dual-mode, JSON output).

### **Phase 7: Answer Generation from Search Results**

This phase focuses on enabling the Web Search Agent (WSA) to synthesize direct answers to user queries from the content of retrieved web pages.

---

Ticket ID: WSA-ANS-001  
Title: Implement `web_content_extractor.py` module  
Description:  
Create the `search_agent/modules/web_content_extractor.py` file. Implement the `async def extract_main_content(url: str) -> str:` function. This function should fetch content using `httpx` and parse HTML with `BeautifulSoup` to extract the main textual content (e.g., from `<article>`, `<main>`, common content divs).

---

Ticket ID: WSA-ANS-002  
Title: Implement content cleaning in `web_content_extractor.py`  
Description:  
Enhance `extract_main_content` to clean extracted text by removing extra whitespace, script tags, and other irrelevant elements.

---

Ticket ID: WSA-ANS-003  
Title: Implement error handling for `web_content_extractor.py`  
Description:  
Add robust error handling for network errors (`httpx.RequestError`, `httpx.TimeoutException`) and HTML parsing issues within `extract_main_content`. Raise custom exceptions like `ScrapingError`.

---

Ticket ID: WSA-ANS-004  
Title: Implement `answer_synthesizer.py` module  
Description:  
Create the `search_agent/answer_synthesizer.py` file. Implement the `async def synthesize_answer(query: str, content_snippets: List[str]) -> str:` function.

---

Ticket ID: WSA-ANS-005  
Title: Develop LLM prompting strategy for `answer_synthesizer.py`  
Description:  
Design and implement the detailed LLM prompt for `synthesize_answer`. The prompt should instruct the LLM to act as an expert summarizer, focus on factual accuracy, avoid hallucination, use only provided content, and be concise.

---

Ticket ID: WSA-ANS-006  
Title: Integrate LLM API call in `answer_synthesizer.py`  
Description:  
Implement the call to the LLM API (e.g., OpenAI's chat completion API) within `synthesize_answer` and extract the synthesized answer.

---

Ticket ID: WSA-ANS-007  
Title: Implement `answer_evaluator.py` module  
Description:  
Create the `search_agent/answer_evaluator.py` file. Implement the `async def evaluate_answer_quality(query: str, synthesized_answer: str, original_content: List[str]) -> Dict[str, Any]:` function.

---

Ticket ID: WSA-ANS-008  
Title: Develop LLM prompting strategy for `answer_evaluator.py`  
Description:  
Design and implement the detailed LLM prompts for `evaluate_answer_quality` to perform factual consistency checks and relevance scoring.

---

Ticket ID: WSA-ANS-009  
Title: Implement NLP-based metrics (optional) in `answer_evaluator.py`  
Description:  
(Optional, but recommended) Implement NLP-based metrics like cosine similarity between query/answer or answer/original content within `evaluate_answer_quality`.

---

Ticket ID: WSA-ANS-010  
Title: Implement `answer_orchestrator.py` module  
Description:  
Create the `search_agent/answer_orchestrator.py` file. Implement the `async def orchestrate_answer_generation(query: str, num_links_to_parse: int = 3) -> Dict[str, Any]:` function.

---

Ticket ID: WSA-ANS-011  
Title: Integrate `search_agent.orchestrator.run_orchestration` call  
Description:  
Implement the call to the existing `search_agent.orchestrator.run_orchestration(query)` within `orchestrate_answer_generation` to get initial search results.

---

Ticket ID: WSA-ANS-012  
Title: Implement link selection logic in `answer_orchestrator.py`  
Description:  
Add logic to `orchestrate_answer_generation` to select the top `N` unique URLs from the ranked search results.

---

Ticket ID: WSA-ANS-013  
Title: Implement web content extraction calls in `answer_orchestrator.py`  
Description:  
Implement the loop to call `web_content_extractor.extract_main_content(url)` for each selected URL within `orchestrate_answer_generation`.

---

Ticket ID: WSA-ANS-014  
Title: Implement content aggregation in `answer_orchestrator.py`  
Description:  
Aggregate the extracted text content from all selected URLs into a single collection.

---

Ticket ID: WSA-ANS-015  
Title: Integrate `answer_synthesizer.synthesize_answer` call  
Description:  
Call `answer_synthesizer.synthesize_answer(query, aggregated_content)` within `orchestrate_answer_generation`.

---

Ticket ID: WSA-ANS-016  
Title: Integrate `answer_evaluator.evaluate_answer_quality` call  
Description:  
Call `answer_evaluator.evaluate_answer_quality(query, synthesized_answer, aggregated_content)` within `orchestrate_answer_generation`.

---

Ticket ID: WSA-ANS-017  
Title: Implement final output structure in `answer_orchestrator.py`  
Description:  
Return a structured object (e.g., `FinalAnswerOutput`) containing the `SynthesizedAnswer` and `AnswerEvaluationResult` objects, along with relevant metadata.

---

Ticket ID: WSA-ANS-018  
Title: Add `SynthesizedAnswer` Pydantic model  
Description:  
Add the `SynthesizedAnswer` Pydantic model to `search_agent/core/models.py` with fields for `answer`, `source_urls`, `timestamp_utc`, and `execution_time_seconds`.

---

Ticket ID: WSA-ANS-019  
Title: Add `AnswerEvaluationResult` Pydantic model  
Description:  
Add the `AnswerEvaluationResult` Pydantic model to `search_agent/core/models.py` with fields for `factual_consistency_score`, `relevance_score`, `completeness_score`, `conciseness_score`, and `llm_feedback`.

---

Ticket ID: WSA-ANS-020  
Title: Add `FinalAnswerOutput` Pydantic model  
Description:  
Add a new Pydantic model `FinalAnswerOutput` to `search_agent/core/models.py` to encapsulate the `SynthesizedAnswer` and `AnswerEvaluationResult` objects, and any other top-level metadata.

---

Ticket ID: WSA-ANS-021  
Title: Implement robust LLM interaction error handling  
Description:  
Implement `try-except` blocks for `openai.APIError`, `openai.RateLimitError`, and other LLM-related exceptions. Include retry mechanisms with exponential backoff.

---

Ticket ID: WSA-ANS-022  
Title: Handle low-quality/error pages during content extraction  
Description:  
Implement logic to flag or skip content if it's too short, irrelevant, or indicates an error page, to prevent feeding low-quality input to the LLM.

---

Ticket ID: WSA-ANS-023  
Title: Graceful handling for no answer generation  
Description:  
Implement logic to gracefully indicate to the user if the LLM fails to synthesize a coherent answer or if no valid content can be extracted from any links.
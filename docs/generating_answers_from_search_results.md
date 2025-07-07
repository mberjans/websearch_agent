# Generating Answers from Search Results: A Detailed Plan

## Executive Summary

This document outlines a comprehensive plan to enhance the Web Search Agent (WSA) system by enabling it to synthesize direct answers to user queries from the content of retrieved web pages. Currently, the WSA provides a ranked list of search results (titles, URLs, snippets). This new functionality will extend that capability by:

1.  **Extracting relevant content** from the web pages linked in the search results.
2.  **Synthesizing a concise answer** to the original query using a Large Language Model (LLM).
3.  **Evaluating the quality** of the synthesized answer for accuracy, completeness, and relevance.
4.  Introducing a **separate orchestration layer** specifically for managing this answer generation and evaluation process.

This enhancement transforms the WSA from a search result aggregator into a question-answering system, providing more direct and actionable information to the user.

## Core Concepts

### 1. Answer Extraction (Web Content Parsing)

This involves programmatically visiting the URLs obtained from the initial search, fetching their content, and intelligently extracting the main textual information relevant to the query. This step is crucial as raw HTML often contains a lot of noise (navigation, ads, footers) that is irrelevant to the core content.

### 2. Answer Synthesis

Once relevant text content is extracted from multiple sources, an LLM will be employed to read through this information, understand the original query, and generate a coherent, concise, and accurate answer. The LLM will act as a "reasoning engine" that distills information from various sources.

### 3. Answer Evaluation

To ensure the quality and trustworthiness of the synthesized answers, a dedicated evaluation mechanism will be implemented. This will assess aspects such as factual consistency with the source material, relevance to the query, completeness, and conciseness. This evaluation can also leverage LLMs, but with a different prompting strategy focused on assessment rather than generation.

### 4. Answer Orchestration

A new, higher-level orchestrator will manage the entire flow: initiating the search, selecting and parsing relevant links, synthesizing the answer, and evaluating it. This keeps the existing search orchestrator focused solely on retrieving and ranking search results, maintaining modularity.

## Architectural Overview

The new components will integrate with the existing system as follows:

```
+-------------------+       +-----------------------+       +---------------------+
| User Query        |------>| Answer Orchestrator   |------>| Search Orchestrator |
+-------------------+       | (NEW)                 |       | (Existing)          |
                            +-----------------------+       +---------------------+
                                    |                                 |
                                    | (Top N Search Results)          | (Calls Search Modules)
                                    V                                 V
                            +-----------------------+       +---------------------+
                            | Web Content Extractor |<------| Search Modules      |
                            | (NEW)                 |       | (Selenium, Playwright, etc.)
                            +-----------------------+       +---------------------+
                                    |
                                    | (Extracted Content from URLs)
                                    V
                            +-----------------------+
                            | Answer Synthesizer    |
                            | (NEW)                 |
                            +-----------------------+
                                    |
                                    | (Synthesized Answer)
                                    V
                            +-----------------------+
                            | Answer Evaluator      |
                            | (NEW)                 |
                            +-----------------------+
                                    |
                                    | (Evaluated Answer + Score)
                                    V
                            +-----------------------+
                            | Final Answer to User  |
                            +-----------------------+
```

## New Components and Modules

### 1. `search_agent/modules/web_content_extractor.py`

This module will be responsible for fetching and parsing the content of individual web pages.

*   **Purpose:** To robustly retrieve the main textual content from a given URL, filtering out boilerplate and irrelevant sections.
*   **Key Function:**
    ```python
    async def extract_main_content(url: str) -> str:
        """
        Fetches the content of a URL and extracts the main textual content.
        Uses httpx for fetching and BeautifulSoup for parsing.
        """
        # Implementation will involve:
        # 1. Async HTTP GET request to the URL.
        # 2. Parsing HTML with BeautifulSoup.
        # 3. Identifying and extracting main content (e.g., <article>, <main>, common content divs).
        # 4. Cleaning extracted text (removing extra whitespace, script tags, etc.).
        pass
    ```
*   **Dependencies:** `httpx`, `BeautifulSoup` (already in `pyproject.toml`).
*   **Error Handling:** Will handle network errors, timeouts, and parsing issues, raising custom exceptions (e.g., `ScrapingError`).

### 2. `search_agent/answer_synthesizer.py`

This module will leverage an LLM to generate a coherent answer from the extracted web content.

*   **Purpose:** To synthesize a direct answer to the user's query based on provided textual content from multiple sources.
*   **Key Function:**
    ```python
    async def synthesize_answer(query: str, content_snippets: List[str]) -> str:
        """
        Synthesizes an answer to the query using an LLM based on provided content snippets.
        """
        # Implementation will involve:
        # 1. Constructing a detailed LLM prompt with the query and content snippets.
        #    Prompt will instruct the LLM to:
        #    - Act as an expert summarizer/answer generator.
        #    - Focus on factual accuracy and direct relevance to the query.
        #    - Avoid hallucination and only use information from provided content.
        #    - Be concise and to the point.
        # 2. Calling the LLM API (e.g., OpenAI's chat completion API).
        # 3. Extracting and returning the synthesized answer.
        pass
    ```
*   **Dependencies:** `openai` (already in `pyproject.toml`).
*   **LLM Prompting Strategy:** The prompt will be carefully engineered to guide the LLM towards factual, concise, and relevant answers, minimizing conversational filler. It will emphasize grounding the answer strictly in the provided `content_snippets`.

### 3. `search_agent/answer_evaluator.py`

This module will assess the quality of the synthesized answer.

*   **Purpose:** To provide an objective (or semi-objective) evaluation of the synthesized answer's quality.
*   **Key Function:**
    ```python
    async def evaluate_answer_quality(query: str, synthesized_answer: str, original_content: List[str]) -> Dict[str, Any]:
        """
        Evaluates the quality of a synthesized answer using an LLM and potentially NLP techniques.
        Returns a dictionary of evaluation metrics (e.g., factual consistency score, relevance score).
        """
        # Implementation will involve:
        # 1. LLM-based factual consistency check: Prompting an LLM to compare the answer against original_content.
        # 2. LLM-based relevance score: Prompting an LLM to score the answer's relevance to the query.
        # 3. (Optional) NLP-based metrics: Cosine similarity between query/answer, answer/original_content.
        # 4. Returning a structured dictionary of scores.
        pass
    ```
*   **Dependencies:** `openai`, `spacy` (already in `pyproject.toml`).
*   **LLM Prompting Strategy:** Prompts will be designed for critical assessment, asking the LLM to identify inconsistencies or irrelevancies.

### 4. `search_agent/answer_orchestrator.py`

This will be the new top-level entry point for generating answers.

*   **Purpose:** To manage the end-to-end process of answer generation, from initial search to final answer synthesis and evaluation.
*   **Key Function:**
    ```python
    async def orchestrate_answer_generation(query: str, num_links_to_parse: int = 3) -> Dict[str, Any]:
        """
        Orchestrates the process of generating a synthesized answer from search results.
        """
        # Implementation will involve:
        # 1. Call search_agent.orchestrator.run_orchestration(query) to get initial search results.
        # 2. Select top N (num_links_to_parse) unique URLs from the search results.
        # 3. For each selected URL, call web_content_extractor.extract_main_content.
        # 4. Aggregate the extracted content.
        # 5. Call answer_synthesizer.synthesize_answer(query, aggregated_content).
        # 6. Call answer_evaluator.evaluate_answer_quality(query, synthesized_answer, aggregated_content).
        # 7. Return the synthesized answer along with evaluation metrics.
        pass
    ```
*   **Integration with Existing Orchestrator:** This new orchestrator will *call* the existing `search_agent/orchestrator.py` to leverage its multi-module search capabilities, de-duplication, and re-ranking of search results. It will not replace it.

## Modified Existing Components

### 1. `search_agent/core/models.py`

New Pydantic models will be added to represent the synthesized answer and its evaluation results, ensuring type safety and consistent data structures.

*   **New Models:**
    ```python
    class SynthesizedAnswer(BaseModel):
        answer: str = Field(..., description="The synthesized answer to the query.")
        source_urls: List[HttpUrl] = Field(..., description="List of URLs from which content was extracted for synthesis.")
        # Add other metadata like timestamp, execution time for answer generation
        timestamp_utc: datetime = Field(..., description="The UTC timestamp of when the answer was synthesized.")
        execution_time_seconds: float = Field(..., description="The total execution time for answer synthesis.")

    class AnswerEvaluationResult(BaseModel):
        factual_consistency_score: float = Field(..., description="Score indicating how consistent the answer is with source content (0-1).")
        relevance_score: float = Field(..., description="Score indicating how relevant the answer is to the original query (0-1).")
        completeness_score: float = Field(..., description="Score indicating how complete the answer is based on available content (0-1).")
        conciseness_score: float = Field(..., description="Score indicating the conciseness of the answer (0-1).")
        # Add LLM feedback if applicable
        llm_feedback: Optional[str] = Field(None, description="Optional textual feedback from the LLM evaluator.")
    ```

## Detailed Workflow for Obtaining and Summarizing Answers

This section specifically addresses your request for a functionality to obtain and summarize answers from the links produced by the current search orchestrator. This will be the primary use case for the `answer_orchestrator.py`.

1.  **User Input:** The user provides a query (e.g., "What is the capital of France?") to the `answer_orchestrator.py` (e.g., via a new Typer CLI command).
2.  **Initial Search:** The `answer_orchestrator.py` internally calls `search_agent.orchestrator.run_orchestration(query)`. This executes all configured search modules (Selenium, Playwright, Brave API, etc.) concurrently, merges their results, de-duplicates them, and re-ranks them. The output is a `SearchModuleOutput` object containing a list of `SearchResult` objects.
3.  **Link Selection:** The `answer_orchestrator.py` selects the top `N` (e.g., 3-5, configurable) `SearchResult` URLs from the ranked list. This `N` can be a parameter to balance comprehensiveness with processing time and cost.
4.  **Web Content Extraction:** For each selected URL:
    *   `answer_orchestrator.py` calls `web_content_extractor.extract_main_content(url)`.
    *   The `web_content_extractor` fetches the page, parses it, and returns the cleaned main text content.
    *   Error handling will be crucial here to gracefully manage broken links, paywalls, or unparseable content.
5.  **Content Aggregation:** The extracted text content from all selected URLs is aggregated into a single collection (e.g., a list of strings).
6.  **Answer Synthesis:** The aggregated content and the original query are passed to `answer_synthesizer.synthesize_answer(query, aggregated_content)`. The LLM processes this input and generates a direct answer.
7.  **Answer Evaluation:** The synthesized answer, the original query, and the aggregated content are passed to `answer_agent/answer_evaluator.py.evaluate_answer_quality(query, synthesized_answer, aggregated_content)`. This returns a set of quality scores and potentially textual feedback.
8.  **Final Output:** The `answer_orchestrator.py` returns a structured object (e.g., a new Pydantic model `FinalAnswerOutput`) containing:
    *   The `SynthesizedAnswer` object (the answer text, source URLs, timestamps).
    *   The `AnswerEvaluationResult` object (quality scores).
    *   Any relevant metadata (e.g., total execution time for the entire answer generation process).

## Error Handling and Robustness

*   **Web Content Extraction:** Implement robust `try-except` blocks for network requests (`httpx.RequestError`, `httpx.TimeoutException`) and HTML parsing (`BeautifulSoup` errors). If a link fails, it should be logged, and the process should continue with other links.
*   **LLM Interaction:** Handle `openai.APIError`, `openai.RateLimitError`, and other potential LLM-related exceptions. Implement retry mechanisms with exponential backoff for transient errors.
*   **Content Quality:** If extracted content is too short, irrelevant, or indicates an error page, it should be flagged or skipped to avoid feeding low-quality input to the LLM.
*   **No Answer Generated:** If the LLM fails to synthesize a coherent answer, or if no valid content can be extracted from any links, the system should gracefully indicate that an answer could not be generated.

## Dependencies

The existing `pyproject.toml` already includes `httpx`, `beautifulsoup4`, `openai`, and `spacy`, which are the primary libraries needed for this new functionality. No new top-level dependencies are anticipated at this stage.

## Future Enhancements

*   **Caching:** Implement caching for fetched web content to avoid re-fetching frequently accessed URLs.
*   **Advanced Content Extraction:** Utilize more sophisticated techniques (e.g., readability libraries, machine learning models) for extracting main content from diverse web page layouts.
*   **Multi-Hop Reasoning:** For complex queries, enable the LLM to perform multi-hop reasoning by iteratively searching and extracting information based on intermediate findings.
*   **User Feedback Loop:** Implement a mechanism for users to provide feedback on answer quality, which can then be used to fine-tune LLM prompts or improve content extraction.
*   **Cost Optimization:** Implement strategies to minimize LLM token usage and API calls, especially for evaluation.

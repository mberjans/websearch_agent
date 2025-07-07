**Category: Web Content Extraction**

*   **WSA-ANS-001: Implement `web_content_extractor.py` module**
    *   **Description:** Create the `search_agent/modules/web_content_extractor.py` file.
    *   **Details:** Implement the `async def extract_main_content(url: str) -> str:` function. This function should fetch content using `httpx` and parse HTML with `BeautifulSoup` to extract the main textual content (e.g., from `<article>`, `<main>`, common content divs).
*   **WSA-ANS-002: Implement content cleaning in `web_content_extractor.py`**
    *   **Description:** Enhance `extract_main_content` to clean extracted text by removing extra whitespace, script tags, and other irrelevant elements.
*   **WSA-ANS-003: Implement error handling for `web_content_extractor.py`**
    *   **Description:** Add robust error handling for network errors (`httpx.RequestError`, `httpx.TimeoutException`) and HTML parsing issues within `extract_main_content`. Raise custom exceptions like `ScrapingError`.

**Category: Answer Synthesis**

*   **WSA-ANS-004: Implement `answer_synthesizer.py` module**
    *   **Description:** Create the `search_agent/answer_synthesizer.py` file.
    *   **Details:** Implement the `async def synthesize_answer(query: str, content_snippets: List[str]) -> str:` function.
*   **WSA-ANS-005: Develop LLM prompting strategy for `answer_synthesizer.py`**
    *   **Description:** Design and implement the detailed LLM prompt for `synthesize_answer`. The prompt should instruct the LLM to act as an expert summarizer, focus on factual accuracy, avoid hallucination, use only provided content, and be concise.
*   **WSA-ANS-006: Integrate LLM API call in `answer_synthesizer.py`**
    *   **Description:** Implement the call to the LLM API (e.g., OpenAI's chat completion API) within `synthesize_answer` and extract the synthesized answer.

**Category: Answer Evaluation**

*   **WSA-ANS-007: Implement `answer_evaluator.py` module**
    *   **Description:** Create the `search_agent/answer_evaluator.py` file.
    *   **Details:** Implement the `async def evaluate_answer_quality(query: str, synthesized_answer: str, original_content: List[str]) -> Dict[str, Any]:` function.
*   **WSA-ANS-008: Develop LLM prompting strategy for `answer_evaluator.py`**
    *   **Description:** Design and implement the detailed LLM prompts for `evaluate_answer_quality` to perform factual consistency checks and relevance scoring.
*   **WSA-ANS-009: Implement NLP-based metrics (optional) in `answer_evaluator.py`**
    *   **Description:** (Optional, but recommended) Implement NLP-based metrics like cosine similarity between query/answer or answer/original content within `evaluate_answer_quality`.

**Category: Answer Orchestration**

*   **WSA-ANS-010: Implement `answer_orchestrator.py` module**
    *   **Description:** Create the `search_agent/answer_orchestrator.py` file.
    *   **Details:** Implement the `async def orchestrate_answer_generation(query: str, num_links_to_parse: int = 3) -> Dict[str, Any]:` function.
*   **WSA-ANS-011: Integrate `search_agent.orchestrator.run_orchestration` call**
    *   **Description:** Implement the call to the existing `search_agent.orchestrator.run_orchestration(query)` within `orchestrate_answer_generation` to get initial search results.
*   **WSA-ANS-012: Implement link selection logic in `answer_orchestrator.py`**
    *   **Description:** Add logic to `orchestrate_answer_generation` to select the top `N` unique URLs from the ranked search results.
*   **WSA-ANS-013: Implement web content extraction calls in `answer_orchestrator.py`**
    *   **Description:** Implement the loop to call `web_content_extractor.extract_main_content(url)` for each selected URL within `orchestrate_answer_generation`.
*   **WSA-ANS-014: Implement content aggregation in `answer_orchestrator.py`**
    *   **Description:** Aggregate the extracted text content from all selected URLs into a single collection.
*   **WSA-ANS-015: Integrate `answer_synthesizer.synthesize_answer` call**
    *   **Description:** Call `answer_synthesizer.synthesize_answer(query, aggregated_content)` within `orchestrate_answer_generation`.
*   **WSA-ANS-016: Integrate `answer_evaluator.evaluate_answer_quality` call**
    *   **Description:** Call `answer_evaluator.evaluate_answer_quality(query, synthesized_answer, aggregated_content)` within `orchestrate_answer_generation`.
*   **WSA-ANS-017: Implement final output structure in `answer_orchestrator.py`**
    *   **Description:** Return a structured object (e.g., `FinalAnswerOutput`) containing the `SynthesizedAnswer` and `AnswerEvaluationResult` objects, along with relevant metadata.

**Category: Data Models**

*   **WSA-ANS-018: Add `SynthesizedAnswer` Pydantic model**
    *   **Description:** Add the `SynthesizedAnswer` Pydantic model to `search_agent/core/models.py` with fields for `answer`, `source_urls`, `timestamp_utc`, and `execution_time_seconds`.
*   **WSA-ANS-019: Add `AnswerEvaluationResult` Pydantic model**
    *   **Description:** Add the `AnswerEvaluationResult` Pydantic model to `search_agent/core/models.py` with fields for `factual_consistency_score`, `relevance_score`, `completeness_score`, `conciseness_score`, and `llm_feedback`.
*   **WSA-ANS-020: Add `FinalAnswerOutput` Pydantic model**
    *   **Description:** Add a new Pydantic model `FinalAnswerOutput` to `search_agent/core/models.py` to encapsulate the `SynthesizedAnswer` and `AnswerEvaluationResult` objects, and any other top-level metadata.

**Category: Robustness and Error Handling (Cross-cutting)**

*   **WSA-ANS-021: Implement robust LLM interaction error handling**
    *   **Description:** Implement `try-except` blocks for `openai.APIError`, `openai.RateLimitError`, and other LLM-related exceptions. Include retry mechanisms with exponential backoff.
*   **WSA-ANS-022: Handle low-quality/error pages during content extraction**
    *   **Description:** Implement logic to flag or skip content if it's too short, irrelevant, or indicates an error page, to prevent feeding low-quality input to the LLM.
*   **WSA-ANS-023: Graceful handling for no answer generation**
    *   **Description:** Implement logic to gracefully indicate to the user if the LLM fails to synthesize a coherent answer or if no valid content can be extracted from any links.

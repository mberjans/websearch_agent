# Checklist for Answer Generation from Search Results

## Category: Web Content Extraction

### WSA-ANS-001: Implement `web_content_extractor.py` module
- [x] WSA-ANS-001-T01: Create `search_agent/modules/web_content_extractor.py` file.
- [x] WSA-ANS-001-T02: Implement `async def extract_main_content(url: str) -> str:` function signature.
- [x] WSA-ANS-001-T03: Add `httpx` for fetching content within `extract_main_content`.
- [x] WSA-ANS-001-T04: Add `BeautifulSoup` for HTML parsing within `extract_main_content`.
- [x] WSA-ANS-001-T05: Implement logic to extract main textual content (e.g., from `<article>`, `<main>`, common content divs).

### WSA-ANS-002: Implement content cleaning in `web_content_extractor.py`
- [x] WSA-ANS-002-T01: Implement removal of extra whitespace from extracted text.
- [x] WSA-ANS-002-T02: Implement removal of script tags from extracted content.
- [x] WSA-ANS-002-T03: Implement removal of style tags from extracted content.

### WSA-ANS-003: Implement error handling for `web_content_extractor.py`
- [x] WSA-ANS-003-T01: Define `ScrapingError` custom exception.
- [x] WSA-ANS-003-T02: Add `try-except` block for `httpx.RequestError`.
- [x] WSA-ANS-003-T03: Add `try-except` block for `httpx.TimeoutException`.
- [x] WSA-ANS-003-T04: Add general `Exception` handling for unexpected errors during HTTP requests.
- [x] WSA-ANS-003-T05: Implement error handling for `BeautifulSoup` parsing issues.
- [x] WSA-ANS-003-T06: Implement graceful handling if main content cannot be found.

## Category: Answer Synthesis

### WSA-ANS-004: Implement `answer_synthesizer.py` module
- [x] WSA-ANS-004-T01: Create `search_agent/answer_synthesizer.py` file.
- [x] WSA-ANS-004-T02: Implement `async def synthesize_answer(query: str, content_snippets: List[str]) -> str:` function signature.

### WSA-ANS-005: Develop LLM prompting strategy for `answer_synthesizer.py`
- [x] WSA-ANS-005-T01: Design initial LLM prompt for `synthesize_answer`.
- [x] WSA-ANS-005-T02: Refine prompt to instruct LLM as an expert summarizer/answer generator.
- [x] WSA-ANS-005-T03: Refine prompt to emphasize factual accuracy and direct relevance.
- [x] WSA-ANS-005-T04: Refine prompt to instruct LLM to avoid hallucination and use only provided content.
- [x] WSA-ANS-005-T05: Refine prompt to instruct LLM to be concise and to the point.

### WSA-ANS-006: Integrate LLM API call in `answer_synthesizer.py`
- [x] WSA-ANS-006-T01: Implement LLM API call (e.g., OpenAI's chat completion API) within `synthesize_answer`.
- [x] WSA-ANS-006-T02: Implement extraction of the synthesized answer from LLM response.

## Category: Answer Evaluation

### WSA-ANS-007: Implement `answer_evaluator.py` module
- [x] WSA-ANS-007-T01: Create `search_agent/answer_evaluator.py` file.
- [x] WSA-ANS-007-T02: Implement `async def evaluate_answer_quality(query: str, synthesized_answer: str, original_content: List[str]) -> Dict[str, Any]:` function signature.

### WSA-ANS-008: Develop LLM prompting strategy for `answer_evaluator.py`
- [x] WSA-ANS-008-T01: Design initial LLM prompt for factual consistency check.
- [x] WSA-ANS-008-T02: Design initial LLM prompt for relevance scoring.
- [x] WSA-ANS-008-T03: Refine prompts for critical assessment and identifying inconsistencies/irrelevancies.

### WSA-ANS-009: Implement NLP-based metrics (optional) in `answer_evaluator.py`
- [x] WSA-ANS-009-T01: Integrate `spacy` library for NLP-based metrics.
- [x] WSA-ANS-009-T02: Implement cosine similarity calculation between query/answer.
- [x] WSA-ANS-009-T03: Implement cosine similarity calculation between answer/original content.

## Category: Answer Orchestration

### WSA-ANS-010: Implement `answer_orchestrator.py` module
- [x] WSA-ANS-010-T01: Create `search_agent/answer_orchestrator.py` file.
- [x] WSA-ANS-010-T02: Implement `async def orchestrate_answer_generation(query: str, num_links_to_parse: int = 3) -> Dict[str, Any]:` function signature.

### WSA-ANS-011: Integrate `search_agent.orchestrator.run_orchestration` call
- [x] WSA-ANS-011-T01: Call `search_agent.orchestrator.run_orchestration(query)` within `orchestrate_answer_generation`.

### WSA-ANS-012: Implement link selection logic in `answer_orchestrator.py`
- [x] WSA-ANS-012-T01: Implement logic to select top `N` unique URLs from search results.

### WSA-ANS-013: Implement web content extraction calls in `answer_orchestrator.py`
- [x] WSA-ANS-013-T01: Implement loop to call `web_content_extractor.extract_main_content(url)` for each selected URL.

### WSA-ANS-014: Implement content aggregation in `answer_orchestrator.py`
- [x] WSA-ANS-014-T01: Aggregate extracted text content from all selected URLs into a single collection.

### WSA-ANS-015: Integrate `answer_synthesizer.synthesize_answer` call
- [x] WSA-ANS-015-T01: Call `answer_synthesizer.synthesize_answer(query, aggregated_content)` within `orchestrate_answer_generation`.

### WSA-ANS-016: Integrate `answer_evaluator.evaluate_answer_quality` call
- [x] WSA-ANS-016-T01: Call `answer_evaluator.evaluate_answer_quality(query, synthesized_answer, aggregated_content)` within `orchestrate_answer_generation`.

### WSA-ANS-017: Implement final output structure in `answer_orchestrator.py`
- [x] WSA-ANS-017-T01: Return a structured object (e.g., `FinalAnswerOutput`) from `orchestrate_answer_generation`.
- [x] WSA-ANS-017-T02: Ensure `SynthesizedAnswer` object is included in the final output.
- [x] WSA-ANS-017-T03: Ensure `AnswerEvaluationResult` object is included in the final output.
- [x] WSA-ANS-017-T04: Include relevant metadata (e.g., total execution time) in the final output.

## Category: Data Models

### WSA-ANS-018: Add `SynthesizedAnswer` Pydantic model
- [x] WSA-ANS-018-T01: Add `SynthesizedAnswer` Pydantic model to `search_agent/core/models.py`.
- [x] WSA-ANS-018-T02: Add `answer` field to `SynthesizedAnswer`.
- [x] WSA-ANS-018-T03: Add `source_urls` field to `SynthesizedAnswer`.
- [x] WSA-ANS-018-T04: Add `timestamp_utc` field to `SynthesizedAnswer`.
- [x] WSA-ANS-018-T05: Add `execution_time_seconds` field to `SynthesizedAnswer`.

### WSA-ANS-019: Add `AnswerEvaluationResult` Pydantic model
- [x] WSA-ANS-019-T01: Add `AnswerEvaluationResult` Pydantic model to `search_agent/core/models.py`.
- [x] WSA-ANS-019-T02: Add `factual_consistency_score` field to `AnswerEvaluationResult`.
- [x] WSA-ANS-019-T03: Add `relevance_score` field to `AnswerEvaluationResult`.
- [x] WSA-ANS-019-T04: Add `completeness_score` field to `AnswerEvaluationResult`.
- [x] WSA-ANS-019-T05: Add `conciseness_score` field to `AnswerEvaluationResult`.
- [x] WSA-ANS-019-T06: Add `llm_feedback` field to `AnswerEvaluationResult`.

### WSA-ANS-020: Add `FinalAnswerOutput` Pydantic model
- [x] WSA-ANS-020-T01: Add `FinalAnswerOutput` Pydantic model to `search_agent/core/models.py`.
- [x] WSA-ANS-020-T02: Ensure `FinalAnswerOutput` encapsulates `SynthesizedAnswer`.
- [x] WSA-ANS-020-T03: Ensure `FinalAnswerOutput` encapsulates `AnswerEvaluationResult`.

## Category: Robustness and Error Handling (Cross-cutting)

### WSA-ANS-021: Implement robust LLM interaction error handling
- [x] WSA-ANS-021-T01: Implement `try-except` blocks for `openai.APIError`.
- [x] WSA-ANS-021-T02: Implement `try-except` blocks for `openai.RateLimitError`.
- [x] WSA-ANS-021-T03: Implement `try-except` blocks for other LLM-related exceptions.
- [x] WSA-ANS-021-T04: Implement retry mechanisms with exponential backoff for transient LLM errors.

### WSA-ANS-022: Handle low-quality/error pages during content extraction
- [x] WSA-ANS-022-T01: Implement logic to flag content if too short.
- [x] WSA-ANS-022-T02: Implement logic to flag content if irrelevant.
- [x] WSA-ANS-022-T03: Implement logic to flag content if it indicates an error page.
- [x] WSA-ANS-022-T04: Implement logic to skip low-quality content to prevent feeding to LLM.

### WSA-ANS-023: Graceful handling for no answer generation
- [x] WSA-ANS-023-T01: Implement logic to detect if LLM fails to synthesize a coherent answer.
- [x] WSA-ANS-023-T02: Implement logic to detect if no valid content can be extracted from any links.
- [x] WSA-ANS-023-T03: Implement graceful indication to the user if no answer can be generated.

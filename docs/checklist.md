### **Phase 7: Answer Generation and Evaluation**

#### **Ticket: WSA-701 - Implement Web Content Extractor**

* [x] **WSA-701-01:** Create the file `search_agent/modules/web_content_extractor.py`.
* [x] **WSA-701-02:** Implement `async def extract_main_content(url: str) -> str` to fetch and parse web content using `httpx` and `BeautifulSoup`.
* [x] **WSA-701-03:** Add robust error handling for network issues and parsing failures.

#### **Ticket: WSA-702 - Implement Answer Synthesizer**

* [ ] **WSA-702-01:** Create the file `search_agent/answer_synthesizer.py`.
* [ ] **WSA-702-02:** Implement `async def synthesize_answer(query: str, content_snippets: List[str]) -> str` using an LLM (e.g., OpenAI).
* [ ] **WSA-702-03:** Design a detailed LLM prompt for accurate and concise answer generation.

#### **Ticket: WSA-703 - Implement Answer Evaluator**

* [ ] **WSA-703-01:** Create the file `search_agent/answer_evaluator.py`.
* [ ] **WSA-703-02:** Implement `async def evaluate_answer_quality(query: str, synthesized_answer: str, original_content: List[str]) -> Dict[str, Any]` using an LLM and/or NLP techniques.
* [ ] **WSA-703-03:** Define metrics for factual consistency, relevance, completeness, and conciseness.

#### **Ticket: WSA-704 - Implement Answer Orchestrator**

* [ ] **WSA-704-01:** Create the file `search_agent/answer_orchestrator.py`.
* [ ] **WSA-704-02:** Implement `async def orchestrate_answer_generation(query: str, num_links_to_parse: int = 3) -> Dict[str, Any]`.
* [ ] **WSA-704-03:** Integrate calls to `search_agent.orchestrator.run_orchestration`, `web_content_extractor`, `answer_synthesizer`, and `answer_evaluator`.
* [ ] **WSA-704-04:** Implement logic for selecting top N links and aggregating content.

#### **Ticket: WSA-705 - Update Core Models**

* [ ] **WSA-705-01:** Modify `search_agent/core/models.py` to add `SynthesizedAnswer` and `AnswerEvaluationResult` Pydantic models.
* [ ] **WSA-705-02:** Include fields for answer text, source URLs, timestamps, execution time, and evaluation scores.

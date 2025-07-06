
import asyncio
from typing import List, Dict, Any, Optional

import spacy
from openai import OpenAI

from search_agent.core.exceptions import SearchAgentError
from search_agent.config import settings

async def evaluate_answer_quality(query: str, synthesized_answer: str, original_content: List[str]) -> Dict[str, Any]:
    """
    Evaluates the quality of a synthesized answer using an LLM and potentially NLP techniques.
    Returns a dictionary of evaluation metrics (e.g., factual consistency score, relevance score).
    """
    evaluation_results = {
        "factual_consistency_score": 0.0,
        "relevance_score": 0.0,
        "completeness_score": 0.0,
        "conciseness_score": 0.0,
        "llm_feedback": None
    }

    # LLM-based evaluation
    if settings.OPENAI_API_KEY:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        combined_original_content = "\n\n---\n\n".join(original_content)

        llm_prompt = f"""You are an expert evaluator of synthesized answers. Your task is to assess the quality of a synthesized answer based on the original query and the source content it was derived from.

Original Query:
"{query}"

Synthesized Answer:
"{synthesized_answer}"

Original Source Content:
---
{combined_original_content}
---

Evaluate the answer based on the following criteria, providing a score from 0.0 to 1.0 for each, and a brief textual feedback.

1.  **Factual Consistency (0.0-1.0):** How well does the synthesized answer align with the facts presented in the original source content? (1.0 = perfectly consistent, 0.0 = completely inconsistent or contains hallucinations)
2.  **Relevance (0.0-1.0):** How relevant is the synthesized answer to the original query? (1.0 = perfectly relevant, 0.0 = completely irrelevant)
3.  **Completeness (0.0-1.0):** How complete is the synthesized answer given the information available in the original source content? (1.0 = covers all key points from source relevant to query, 0.0 = misses crucial information)
4.  **Conciseness (0.0-1.0):** How concise is the synthesized answer without losing important information? (1.0 = perfectly concise, 0.0 = overly verbose or too brief)

Provide your evaluation in a JSON format with the following keys: `factual_consistency_score`, `relevance_score`, `completeness_score`, `conciseness_score`, and `llm_feedback` (a string).

Example JSON output:
{{"factual_consistency_score": 0.9, "relevance_score": 0.8, "completeness_score": 0.7, "conciseness_score": 0.9, "llm_feedback": "The answer is mostly accurate but could be more comprehensive."}}

JSON Evaluation:"""

        try:
            response = await client.chat.completions.create(
                model=settings.LLM_EVALUATOR_MODEL,
                messages=[
                    {"role": "user", "content": llm_prompt}
                ],
                response_format={ "type": "json_object" },
                max_tokens=500,
                temperature=0.0,
            )
            llm_output = response.choices[0].message.content
            import json
            parsed_llm_output = json.loads(llm_output)

            evaluation_results["factual_consistency_score"] = parsed_llm_output.get("factual_consistency_score", 0.0)
            evaluation_results["relevance_score"] = parsed_llm_output.get("relevance_score", 0.0)
            evaluation_results["completeness_score"] = parsed_llm_output.get("completeness_score", 0.0)
            evaluation_results["conciseness_score"] = parsed_llm_output.get("conciseness_score", 0.0)
            evaluation_results["llm_feedback"] = parsed_llm_output.get("llm_feedback")

        except Exception as e:
            evaluation_results["llm_feedback"] = f"LLM evaluation failed: {e}"

    # NLP-based evaluation (Cosine Similarity)
    try:
        nlp = spacy.load("en_core_web_md")
        query_doc = nlp(query)
        answer_doc = nlp(synthesized_answer)
        
        # Ensure docs have vectors before calculating similarity
        if query_doc.has_vector and answer_doc.has_vector:
            evaluation_results["nlp_relevance_score"] = query_doc.similarity(answer_doc)
        else:
            evaluation_results["nlp_relevance_score"] = 0.0 # Or handle as error

    except OSError:
        evaluation_results["llm_feedback"] = (evaluation_results["llm_feedback"] or "") + \
                                            "spaCy model 'en_core_web_md' not found. Please install it with: python -m spacy download en_core_web_md"
    except Exception as e:
        evaluation_results["llm_feedback"] = (evaluation_results["llm_feedback"] or "") + f"NLP evaluation failed: {e}"

    return evaluation_results


import asyncio
from typing import List

from openai import OpenAI

from search_agent.core.exceptions import SearchAgentError
from search_agent.config import settings

async def synthesize_answer(query: str, content_snippets: List[str]) -> str:
    """
    Synthesizes an answer to the query using an LLM based on provided content snippets.
    """
    if not settings.OPENAI_API_KEY:
        raise SearchAgentError("OPENAI_API_KEY is not configured in settings for answer synthesis.")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Combine content snippets into a single string
    combined_content = "\n\n---\n\n".join(content_snippets)

    # Construct the prompt for the LLM
    prompt = f"""You are an expert assistant tasked with synthesizing a concise and accurate answer to a user's query based on provided text snippets.

Here's the user's query:
"{query}"

Here are the text snippets from various web pages. Use ONLY the information present in these snippets to formulate your answer. Do NOT use any outside knowledge.

---
{combined_content}
---

Based on the query and the provided snippets, please synthesize a direct, concise, and factual answer. If the snippets do not contain enough information to answer the query, state that clearly.

Synthesized Answer:"""

    try:
        response = await client.chat.completions.create(
            model=settings.LLM_EVALUATOR_MODEL, # Reusing the evaluator model for now
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500, # Limit answer length
            temperature=0.2, # Keep it factual and less creative
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise SearchAgentError(f"LLM answer synthesis failed: {e}")

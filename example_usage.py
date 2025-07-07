#!/usr/bin/env python3
"""
Simple example showing how to use the websearch agent as a module.

This script demonstrates the most common use case: asking a question
and getting a comprehensive answer with sources.
"""

import asyncio
from search_agent.config import Configuration, SearchConfig, LLMConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation


async def get_answer(question: str, max_sources: int = 3):
    """
    Get a comprehensive answer to a question using web search.
    
    Args:
        question: The question to answer
        max_sources: Maximum number of sources to extract content from
        
    Returns:
        Dictionary containing the answer and metadata
    """
    # Create configuration
    config = Configuration(
        query=question,
        search=SearchConfig(
            provider="selenium",
            max_results=10,
            max_urls=max_sources
        ),
        llm=LLMConfig(
            provider="openrouter",
            model="openrouter/cypher-alpha:free"
        )
    )
    
    # Run the search and answer generation
    result = await orchestrate_answer_generation(
        query=config.query,
        num_links_to_parse=config.search.max_urls,
        config=config
    )
    
    return result


def main():
    """Example usage of the websearch agent."""
    
    # Example questions
    questions = [
        "What is the impact of climate change on biodiversity?",
        "How do vaccines work to protect against diseases?",
        "What are the latest developments in renewable energy technology?"
    ]
    
    print("🔍 WebSearch Agent - Example Usage")
    print("=" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 Question {i}: {question}")
        print("-" * 50)
        
        try:
            # Get the answer
            result = asyncio.run(get_answer(question))
            
            # Display results
            print(f"✅ Answer generated in {result['execution_time_seconds']:.2f} seconds")
            print(f"📚 Sources used: {len(result['source_urls'])}")
            print(f"📊 Quality scores:")
            
            if 'evaluation_results' in result:
                scores = result['evaluation_results']
                print(f"   - Factual Consistency: {scores.get('factual_consistency_score', 'N/A')}")
                print(f"   - Relevance: {scores.get('relevance_score', 'N/A')}")
                print(f"   - Completeness: {scores.get('completeness_score', 'N/A')}")
                print(f"   - Conciseness: {scores.get('conciseness_score', 'N/A')}")
            
            print(f"\n💡 Answer:")
            print(result['synthesized_answer']['answer'])
            
            print(f"\n🔗 Sources:")
            for url in result['source_urls']:
                print(f"   - {url}")
                
        except Exception as e:
            print(f"❌ Error processing question: {e}")
        
        print("\n" + "=" * 50)


if __name__ == "__main__":
    main() 
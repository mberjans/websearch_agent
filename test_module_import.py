#!/usr/bin/env python3
"""
Test script demonstrating how to import and use the websearch agent as a module.

This script shows different ways to use the websearch agent:
1. Basic usage with the main function
2. Direct module usage
3. Configuration usage
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Import the websearch agent modules
from search_agent.config import Configuration, SearchConfig, LLMConfig, AdvancedConfig
from search_agent.answer_orchestrator import orchestrate_answer_generation
from search_agent.modules.selenium_search import search as selenium_search
from search_agent.modules.web_content_extractor import extract_main_content


def setup_logging():
    """Setup logging for the test script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_basic_usage():
    """Test 1: Basic usage with the main orchestration function."""
    print("\n" + "="*60)
    print("TEST 1: Basic Usage with Main Orchestration")
    print("="*60)
    
    try:
        # Create a simple configuration
        config = Configuration(
            query="What is artificial intelligence?",
            search=SearchConfig(
                provider="selenium",
                max_results=3,
                max_urls=2
            ),
            llm=LLMConfig(
                provider="openrouter",
                model="openrouter/cypher-alpha:free"
            )
        )
        
        # Run the orchestration
        result = asyncio.run(orchestrate_answer_generation(
            query=config.query,
            num_links_to_parse=config.search.max_urls,
            config=config
        ))
        
        print(f"✅ Success! Answer generated:")
        print(f"Query: {config.query}")
        print(f"Answer: {result['synthesized_answer']['answer']}")
        print(f"Sources: {len(result['source_urls'])} URLs")
        print(f"Execution time: {result['execution_time_seconds']:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic usage test: {e}")
        return False


def test_direct_module_usage():
    """Test 2: Direct module usage without orchestrator."""
    print("\n" + "="*60)
    print("TEST 2: Direct Module Usage")
    print("="*60)
    
    try:
        # Test direct search module usage
        query = "What is machine learning?"
        search_results = await selenium_search(query)
        
        print(f"✅ Direct search module test:")
        print(f"Query: {query}")
        print(f"Found {len(search_results)} search results")
        
        if search_results:
            print(f"First result: {search_results[0].title}")
            print(f"First URL: {search_results[0].url}")
        
        # Test direct content extraction
        if search_results:
            url = str(search_results[0].url)
            content = asyncio.run(extract_main_content(url))
            
            if content:
                print(f"✅ Content extraction successful:")
                print(f"Extracted {len(content)} characters")
                print(f"Preview: {content[:200]}...")
            else:
                print("❌ Content extraction failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in direct module usage test: {e}")
        return False


def test_custom_configuration():
    """Test 3: Custom configuration with specific settings."""
    print("\n" + "="*60)
    print("TEST 3: Custom Configuration")
    print("="*60)
    
    try:
        # Create custom configuration
        config = Configuration(
            query="What are the latest developments in quantum computing?",
            search=SearchConfig(
                provider="selenium",
                max_results=5,
                max_urls=3,
                timeout=10
            ),
            llm=LLMConfig(
                provider="openrouter",
                model="openrouter/cypher-alpha:free",
                temperature=0.7,
                max_tokens=1000
            ),
            advanced=AdvancedConfig(
                user_agent="Custom Test Agent/1.0",
                debug=True
            )
        )
        
        # Run the orchestration
        result = asyncio.run(orchestrate_answer_generation(
            query=config.query,
            num_links_to_parse=config.search.max_urls,
            config=config
        ))
        
        print(f"✅ Success! Custom configuration test:")
        print(f"Query: {config.query}")
        print(f"Answer: {result['synthesized_answer']['answer'][:200]}...")
        print(f"Sources: {len(result['source_urls'])} URLs")
        print(f"Evaluation scores: {result['evaluation_results']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in custom configuration test: {e}")
        return False


def test_batch_processing():
    """Test 4: Batch processing multiple queries."""
    print("\n" + "="*60)
    print("TEST 4: Batch Processing")
    print("="*60)
    
    queries = [
        "What is blockchain technology?",
        "How does photosynthesis work?",
        "What are the benefits of exercise?"
    ]
    
    results = []
    
    try:
        for i, query in enumerate(queries, 1):
            print(f"\nProcessing query {i}/{len(queries)}: {query}")
            
            config = Configuration(
                query=query,
                search=SearchConfig(
                    provider="selenium",
                    max_results=3,
                    max_urls=2
                ),
                llm=LLMConfig(
                    provider="openrouter",
                    model="openrouter/cypher-alpha:free"
                )
            )
            
            result = asyncio.run(orchestrate_answer_generation(
                query=config.query,
                num_links_to_parse=config.search.max_urls,
                config=config
            ))
            
            results.append({
                'query': query,
                'answer': result['synthesized_answer']['answer'],
                'sources': len(result['source_urls']),
                'execution_time': result['execution_time_seconds']
            })
            
            print(f"✅ Query {i} completed in {result['execution_time_seconds']:.2f}s")
        
        print(f"\n✅ Batch processing completed:")
        print(f"Processed {len(results)} queries successfully")
        
        for i, result in enumerate(results, 1):
            print(f"Query {i}: {result['query']}")
            print(f"  Answer: {result['answer'][:100]}...")
            print(f"  Sources: {result['sources']}, Time: {result['execution_time']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in batch processing test: {e}")
        return False


def test_save_and_load_results():
    """Test 5: Save and load results."""
    print("\n" + "="*60)
    print("TEST 5: Save and Load Results")
    print("="*60)
    
    try:
        # Generate a result
        config = Configuration(
            query="What is the future of renewable energy?",
            search=SearchConfig(
                provider="selenium",
                max_results=3,
                max_urls=2
            ),
            llm=LLMConfig(
                provider="openrouter",
                model="openrouter/cypher-alpha:free"
            )
        )
        
        result = asyncio.run(orchestrate_answer_generation(
            query=config.query,
            num_links_to_parse=config.search.max_urls,
            config=config
        ))
        
        # Save result to file
        output_file = Path("test_output.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"✅ Result saved to {output_file}")
        
        # Load result from file
        with open(output_file, 'r') as f:
            loaded_data = json.load(f)
        
        print(f"✅ Result loaded from {output_file}")
        print(f"Query: {loaded_data['query']}")
        print(f"Answer: {loaded_data['synthesized_answer']['answer'][:100]}...")
        
        # Clean up
        output_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in save/load test: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting WebSearch Agent Module Import Tests")
    print("="*60)
    
    setup_logging()
    
    tests = [
        ("Basic Usage", test_basic_usage),
        ("Direct Module Usage", test_direct_module_usage),
        ("Custom Configuration", test_custom_configuration),
        ("Batch Processing", test_batch_processing),
        ("Save and Load Results", test_save_and_load_results),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("🎉 All tests passed! The module is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
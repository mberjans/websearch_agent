import pytest
from search_agent.config import Configuration, SearchConfig, LLMConfig


def test_merge_single_configuration():
    """Test merging a single configuration (should return the same config)."""
    config1 = Configuration(query="test query")
    merged = Configuration.merge_configurations(config1)
    assert merged.query == "test query"
    assert merged is not config1  # Should be a new instance


def test_merge_two_configurations():
    """Test merging two configurations with different values."""
    config1 = Configuration(
        query="original query",
        search=SearchConfig(provider="selenium", max_results=5)
    )
    config2 = Configuration(
        query="override query",
        search=SearchConfig(provider="playwright", max_results=10)
    )
    
    merged = Configuration.merge_configurations(config1, config2)
    
    # Later config should override earlier config
    assert merged.query == "override query"
    assert merged.search.provider == "playwright"
    assert merged.search.max_results == 10


def test_merge_three_configurations():
    """Test merging three configurations with priority order."""
    config1 = Configuration(
        query="base query",
        search=SearchConfig(provider="selenium", max_results=5),
        llm=LLMConfig(provider="openai", temperature=0.1)
    )
    config2 = Configuration(
        query="override1 query",
        search=SearchConfig(provider="playwright", max_results=10),
        llm=LLMConfig(provider="anthropic", temperature=0.5)
    )
    config3 = Configuration(
        query="override2 query",
        search=SearchConfig(provider="brave", max_results=15)
    )
    
    merged = Configuration.merge_configurations(config1, config2, config3)
    
    # Latest config should have highest priority
    assert merged.query == "override2 query"
    assert merged.search.provider == "brave"
    assert merged.search.max_results == 15
    assert merged.llm.provider == "openrouter"  # From config3 (default, since not specified)


def test_merge_nested_configurations():
    """Test merging configurations with nested structures."""
    config1 = Configuration(
        query="base query",
        search=SearchConfig(
            provider="selenium",
            max_results=5,
            timeout=30
        ),
        llm=LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            temperature=0.1
        )
    )
    config2 = Configuration(
        query="override query",
        search=SearchConfig(
            provider="playwright",
            max_results=10
        ),
        llm=LLMConfig(
            provider="anthropic",
            model="gpt-4",
            temperature=0.5
        )
    )
    
    merged = Configuration.merge_configurations(config1, config2)
    
    # Nested values should be merged correctly
    assert merged.query == "override query"
    assert merged.search.provider == "playwright"
    assert merged.search.max_results == 10
    assert merged.search.timeout == 30
    assert merged.llm.provider == "anthropic"
    assert merged.llm.model == "gpt-4"
    assert merged.llm.temperature == 0.5


def test_merge_with_defaults():
    """Test merging with default configuration values."""
    config1 = Configuration(query="test query")  # Uses all defaults
    config2 = Configuration(
        query="override query",
        search=SearchConfig(provider="brave")
    )
    
    merged = Configuration.merge_configurations(config1, config2)
    
    assert merged.query == "override query"
    assert merged.search.provider == "brave"
    # Should use defaults for other values
    assert merged.search.max_results == 10  # Default value
    assert merged.llm.provider == "openrouter"  # Default value


def test_merge_empty_configurations():
    """Test merging configurations with minimal data."""
    config1 = Configuration(query="")
    config2 = Configuration(query="test")
    
    merged = Configuration.merge_configurations(config1, config2)
    assert merged.query == "test"


def test_merge_no_configurations():
    """Test that merging with no configurations raises an error."""
    with pytest.raises(ValueError, match="At least one configuration must be provided"):
        Configuration.merge_configurations()


def test_deep_merge_dictionaries():
    """Test the _deep_merge method with nested dictionaries."""
    base = {
        "a": 1,
        "b": {"x": 10, "y": 20},
        "c": {"nested": {"deep": "value"}}
    }
    override = {
        "a": 2,
        "b": {"y": 25, "z": 30},
        "c": {"nested": {"deep": "new_value", "extra": "data"}}
    }
    
    merged = Configuration._deep_merge(base, override)
    
    assert merged["a"] == 2  # Simple override
    assert merged["b"]["x"] == 10  # Preserved from base
    assert merged["b"]["y"] == 25  # Overridden
    assert merged["b"]["z"] == 30  # New from override
    assert merged["c"]["nested"]["deep"] == "new_value"  # Deep override
    assert merged["c"]["nested"]["extra"] == "data"  # New deep value


def test_deep_merge_lists():
    """Test the _deep_merge method with lists."""
    base = {
        "items": [1, 2, 3],
        "nested": {"list": [10, 20]}
    }
    override = {
        "items": [4, 5],
        "nested": {"list": [30]}
    }
    
    merged = Configuration._deep_merge(base, override)
    
    # Lists should be replaced, not extended
    assert merged["items"] == [4, 5]
    assert merged["nested"]["list"] == [30]


def test_deep_merge_sets():
    """Test the _deep_merge method with sets."""
    base = {
        "items": {1, 2, 3},
        "nested": {"set": {10, 20}}
    }
    override = {
        "items": {4, 5},
        "nested": {"set": {30}}
    }
    
    merged = Configuration._deep_merge(base, override)
    
    # Sets should be replaced, not unioned
    assert merged["items"] == {4, 5}
    assert merged["nested"]["set"] == {30}


def test_deep_merge_mixed_types():
    """Test the _deep_merge method with mixed data types."""
    base = {
        "string": "hello",
        "number": 42,
        "boolean": True,
        "list": [1, 2],
        "dict": {"a": 1},
        "none": None
    }
    override = {
        "string": "world",
        "number": 100,
        "boolean": False,
        "list": [3, 4],
        "dict": {"b": 2},
        "none": "not none"
    }
    
    merged = Configuration._deep_merge(base, override)
    
    assert merged["string"] == "world"
    assert merged["number"] == 100
    assert merged["boolean"] is False
    assert merged["list"] == [3, 4]
    assert merged["dict"]["a"] == 1  # Preserved
    assert merged["dict"]["b"] == 2  # Added
    assert merged["none"] == "not none" 
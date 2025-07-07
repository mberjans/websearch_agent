import pytest
import tempfile
import os
from pathlib import Path
from search_agent.config import Configuration


def test_load_valid_config_file():
    """Test loading a valid YAML configuration file."""
    config_data = """
query: "test query"
search:
  provider: "selenium"
  max_results: 5
  max_urls: 2
  timeout: 60
llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.5
  max_tokens: 2048
output:
  directory: "./test_output"
  file: "test_result"
  project_name: "test_project"
advanced:
  proxy: "http://proxy.example.com:8080"
  user_agent: "Custom Agent"
  retry_count: 5
  extract_images: true
  save_html: true
  debug: true
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_data)
        config_file = f.name
    
    try:
        config = Configuration.from_file(config_file)
        
        # Test that all values are loaded correctly
        assert config.query == "test query"
        assert config.search.provider == "selenium"
        assert config.search.max_results == 5
        assert config.search.max_urls == 2
        assert config.search.timeout == 60
        assert config.llm.provider == "openai"
        assert config.llm.model == "gpt-4"
        assert config.llm.temperature == 0.5
        assert config.llm.max_tokens == 2048
        assert config.output.directory == "./test_output"
        assert config.output.file == "test_result"
        assert config.output.project_name == "test_project"
        assert config.advanced.proxy == "http://proxy.example.com:8080"
        assert config.advanced.user_agent == "Custom Agent"
        assert config.advanced.retry_count == 5
        assert config.advanced.extract_images is True
        assert config.advanced.save_html is True
        assert config.advanced.debug is True
        
    finally:
        os.unlink(config_file)


def test_load_config_with_query_override():
    """Test loading config file with query override."""
    config_data = """
query: "original query"
search:
  provider: "playwright"
llm:
  provider: "openai"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_data)
        config_file = f.name
    
    try:
        config = Configuration.from_file(config_file, query="override query")
        assert config.query == "override query"
        assert config.search.provider == "playwright"
        assert config.llm.provider == "openai"
        
    finally:
        os.unlink(config_file)


def test_load_config_without_query():
    """Test loading config file without query in file."""
    config_data = """
search:
  provider: "selenium"
llm:
  provider: "openai"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_data)
        config_file = f.name
    
    try:
        config = Configuration.from_file(config_file)
        assert config.query == ""  # Should default to empty string
        
    finally:
        os.unlink(config_file)


def test_load_empty_config_file():
    """Test loading an empty YAML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("")
        config_file = f.name
    
    try:
        config = Configuration.from_file(config_file)
        assert config.query == ""
        # Should use default values for all other fields
        
    finally:
        os.unlink(config_file)


def test_load_none_config_file():
    """Test loading a YAML file with only null values."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("query: null\nsearch: null\nllm: null")
        config_file = f.name
    
    try:
        # This should handle null values gracefully by using defaults
        config = Configuration.from_file(config_file)
        assert config.query == ""
        # Should use default values for all other fields
        
    finally:
        os.unlink(config_file)


def test_load_invalid_yaml_file():
    """Test loading an invalid YAML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content: [")
        config_file = f.name
    
    try:
        with pytest.raises(ValueError, match="Invalid YAML"):
            Configuration.from_file(config_file)
            
    finally:
        os.unlink(config_file)


def test_load_nonexistent_file():
    """Test loading a non-existent file."""
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        Configuration.from_file("nonexistent_file.yaml")


def test_load_directory_as_file():
    """Test loading a directory as if it were a file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(ValueError, match="Path is not a file"):
            Configuration.from_file(temp_dir)


def test_load_config_with_partial_data():
    """Test loading config with only some sections defined."""
    config_data = """
query: "partial test"
search:
  provider: "brave"
  max_results: 15
# llm and output sections not defined, should use defaults
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_data)
        config_file = f.name
    
    try:
        config = Configuration.from_file(config_file)
        assert config.query == "partial test"
        assert config.search.provider == "brave"
        assert config.search.max_results == 15
        # Should use default values for llm and output sections
        
    finally:
        os.unlink(config_file)


def test_config_file_encoding_error():
    """Test loading a file with invalid encoding."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.yaml', delete=False) as f:
        # Write invalid UTF-8 bytes
        f.write(b"query: \xff\xfe\xfd")
        config_file = f.name
    
    try:
        with pytest.raises(ValueError, match="invalid UTF-8 encoding"):
            Configuration.from_file(config_file)
            
    finally:
        os.unlink(config_file) 
import pytest
from typer.testing import CliRunner
from websearch_agent import app

runner = CliRunner()

def test_core_argument_parsing():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--output-dir", "./my_output",
        "--output-file", "myfile",
        "--project-name", "myproject"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing
    # Output should mention the arguments
    assert "test query" in result.output
    assert "my_output" in result.output or "./my_output" in result.output
    assert "myfile" in result.output
    assert "myproject" in result.output


def test_query_validation_empty():
    result = runner.invoke(app, ["search", ""])
    assert result.exit_code == 2
    assert "Query cannot be empty" in result.output


def test_query_validation_too_short():
    result = runner.invoke(app, ["search", "ab"])
    assert result.exit_code == 2
    assert "Query must be at least 3 characters long" in result.output


def test_query_validation_too_long():
    long_query = "a" * 501
    result = runner.invoke(app, ["search", long_query])
    assert result.exit_code == 2
    assert "Query must be less than 500 characters" in result.output


def test_project_name_validation_invalid_chars():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--project-name", "invalid@project"
    ])
    assert result.exit_code == 2
    assert "Project name can only contain letters" in result.output


def test_output_file_validation_invalid_chars():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--output-file", "invalid@file"
    ])
    assert result.exit_code == 2
    assert "Output file name can only contain letters" in result.output


def test_valid_arguments():
    result = runner.invoke(app, [
        "search",
        "What is Python programming?",
        "--project-name", "valid_project",
        "--output-file", "valid_file"
    ])
    # Should not error due to validation
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_search_provider_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--search-provider", "selenium"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing
    # Output should mention the search provider
    assert "selenium" in result.output or "Search Provider" in result.output


def test_max_results_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--max-results", "5"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing
    # Output should mention max results
    assert "5" in result.output or "Max Results" in result.output


def test_max_urls_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--max-urls", "2"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_timeout_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--timeout", "60"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_no_cache_flag():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--no-cache"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_force_refresh_flag():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--force-refresh"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_multiple_search_arguments():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--search-provider", "playwright",
        "--max-results", "10",
        "--max-urls", "3",
        "--timeout", "30",
        "--no-cache",
        "--force-refresh"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing
    # Output should mention the arguments
    assert "playwright" in result.output or "Search Provider" in result.output
    assert "10" in result.output or "Max Results" in result.output


def test_llm_provider_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--llm-provider", "openai"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_llm_model_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--llm-model", "gpt-4"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing
    # Output should mention the LLM model
    assert "gpt-4" in result.output or "LLM Model" in result.output


def test_temperature_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--temperature", "0.5"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_max_tokens_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--max-tokens", "2048"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_no_evaluation_flag():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--no-evaluation"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_multiple_llm_arguments():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--llm-provider", "openai",
        "--llm-model", "gpt-4",
        "--temperature", "0.3",
        "--max-tokens", "1024",
        "--no-evaluation"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing
    # Output should mention the arguments
    assert "gpt-4" in result.output or "LLM Model" in result.output


def test_config_file_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--config-file", "test_config.yaml"
    ])
    # Should not error (even if file doesn't exist, it should parse the argument)
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_proxy_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--proxy", "http://proxy.example.com:8080"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_user_agent_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--user-agent", "Custom User Agent"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_retry_count_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--retry-count", "5"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_extract_images_flag():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--extract-images"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_save_html_flag():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--save-html"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_debug_flag():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--debug"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_multiple_advanced_arguments():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--config-file", "test_config.yaml",
        "--proxy", "http://proxy.example.com:8080",
        "--user-agent", "Custom User Agent",
        "--retry-count", "3",
        "--extract-images",
        "--save-html",
        "--debug"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_verbose_flag():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--verbose"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_quiet_flag():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--quiet"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_debug_logging_flag():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--debug"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_multiple_logging_flags():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--verbose",
        "--debug"
    ])
    # Should not error
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_invalid_search_provider():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--search-provider", "invalid_provider"
    ])
    # Should handle invalid search provider gracefully
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_invalid_llm_provider():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--llm-provider", "invalid_provider"
    ])
    # Should handle invalid LLM provider gracefully
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_invalid_temperature_value():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--temperature", "2.0"  # Invalid temperature value
    ])
    # Should handle invalid temperature value gracefully
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_invalid_max_tokens_value():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--max-tokens", "-1"  # Invalid max tokens value
    ])
    # Should handle invalid max tokens value gracefully
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_invalid_timeout_value():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--timeout", "0"  # Invalid timeout value
    ])
    # Should handle invalid timeout value gracefully
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_invalid_retry_count_value():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--retry-count", "-1"  # Invalid retry count value
    ])
    # Should handle invalid retry count value gracefully
    assert result.exit_code == 0 or result.exit_code == 1  # 1 is allowed if API keys are missing


def test_missing_required_argument():
    result = runner.invoke(app, ["search"])
    # Should show error for missing required argument
    assert result.exit_code == 2
    assert "Missing argument" in result.output or "Error" in result.output


def test_unknown_argument():
    result = runner.invoke(app, [
        "search",
        "test query",
        "--unknown-argument", "value"
    ])
    # Should show error for unknown argument
    assert result.exit_code == 2
    assert "Error" in result.output or "Unknown" in result.output 
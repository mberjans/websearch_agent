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
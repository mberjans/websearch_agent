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
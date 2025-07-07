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
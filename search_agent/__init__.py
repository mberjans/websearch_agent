"""
Clinical Metabolomics Oracle Web Search Agent

A comprehensive web search and answer generation tool that combines
multiple search providers with LLM-powered answer synthesis.
"""

__version__ = "1.0.0"
__author__ = "Clinical Metabolomics Oracle Team"
__description__ = "Clinical Metabolomics Oracle Web Search Agent"

from .config import Configuration
from .answer_orchestrator import orchestrate_answer_generation

__all__ = [
    "Configuration",
    "orchestrate_answer_generation",
    "__version__",
    "__author__",
    "__description__"
]
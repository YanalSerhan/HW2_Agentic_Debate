"""Auto-generated docstring."""

import os
from unittest.mock import MagicMock

import pytest

# Ensure no real API calls are made during tests by keeping api_key falsy
os.environ["ANTHROPIC_API_KEY"] = ""

@pytest.fixture
def anthropic_response_factory():
    """Auto-generated docstring."""
    class AnthropicContentBlock:
        """Auto-generated docstring."""

        def __init__(self, t, n="", text="Mock text", results=None):
            """Auto-generated docstring."""
            self.type = t
            self.name = n
            self.text = text
            self.input = {"query": "mock"}
            self.id = "fake_id"
            if results is not None:
                self.results = results

    class AnthropicAPIResponse:
        """Auto-generated docstring."""

        def __init__(self, content):
            """Auto-generated docstring."""
            self.content = content
            self.usage = type('obj', (object,), {'input_tokens': 10, 'output_tokens': 10})()

    return AnthropicContentBlock, AnthropicAPIResponse

@pytest.fixture
def fake_anthropic_client(anthropic_response_factory):
    """Auto-generated docstring."""
    AnthropicContentBlock, AnthropicAPIResponse = anthropic_response_factory  # noqa: N806
    client = MagicMock()
    # Provide a default return_value for a single step call with web search results
    client.messages.create.return_value = AnthropicAPIResponse([
        AnthropicContentBlock("web_search_tool_result", results=[{"url": "mock://search", "title": "Mock title", "snippet": "Mock snippet"}]),
        AnthropicContentBlock("text", text="Mock response")
    ])
    return client

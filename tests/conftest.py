import os
import pytest
from unittest.mock import MagicMock

# Ensure no real API calls are made during tests by keeping api_key falsy
os.environ["ANTHROPIC_API_KEY"] = ""

@pytest.fixture
def anthropic_response_factory():
    class AnthropicContentBlock:
        def __init__(self, t, n="", text="Mock text", results=None):
            self.type = t
            self.name = n
            self.text = text
            self.input = {"query": "mock"}
            self.id = "fake_id"
            if results is not None:
                self.results = results
            
    class AnthropicAPIResponse:
        def __init__(self, content):
            self.content = content
            self.usage = type('obj', (object,), {'input_tokens': 10, 'output_tokens': 10})()
            
    return AnthropicContentBlock, AnthropicAPIResponse

@pytest.fixture
def fake_anthropic_client(anthropic_response_factory):
    AnthropicContentBlock, AnthropicAPIResponse = anthropic_response_factory
    client = MagicMock()
    # Provide a default return_value for a single step call with web search results
    client.messages.create.return_value = AnthropicAPIResponse([
        AnthropicContentBlock("web_search_tool_result", results=[{"url": "mock://search", "title": "Mock title", "snippet": "Mock snippet"}]),
        AnthropicContentBlock("text", text="Mock response")
    ])
    return client

"""Auto-generated docstring."""

from unittest.mock import MagicMock

from debate.services.agents.api_mixin import ApiMixin


class DummyAgent(ApiMixin):
    """Auto-generated docstring."""

    def __init__(self):
        """Auto-generated docstring."""
        self.gatekeeper = MagicMock()
        self.config = {}

    def log_api_call(self, prompt_tokens, completion_tokens, cost_usd):
        """Auto-generated docstring."""
        pass


def test_api_mixin_cleanup():
    """Auto-generated docstring."""
    agent = DummyAgent()

    examples = [
        (
            "I need to search for evidence... Let me gather some facts.\n---\nThe real argument begins here.",
            "The real argument begins here."
        ),
        (
            "Excellent. I have the ammunition. --- The real argument begins here.",
            "The real argument begins here."
        ),
        (
            "Now let me search for that. \n\n--- \nThis is a solid argument. Excellent point made by the opponent.",
            "This is a solid argument. Excellent point made by the opponent."
        ),
        (
            "I will search now. Let's search. \nThis is the argument. I have the evidence to prove it.",
            "This is the argument. I have the evidence to prove it."
        ),
        (
            "I'll need to arm myself with evidence before I dismantle this carefully constructed evasion. Let me search the empirical record.---\nThe argument begins.",
            "The argument begins."
        ),
        (
            "I need to search for substantive evidence on religion's societal impact—both positive and negative—to mount a proper Hitchensian counter-argument. Let me gather some facts.---\nThe argument begins.",
            "The argument begins."
        ),
        (
            "No narration here. Just a normal argument. Excellent.",
            "No narration here. Just a normal argument. Excellent."
        )
    ]

    for raw_text, expected in examples:
        class MockBlock:
            """Auto-generated docstring."""

            def __init__(self, t, text):
                """Auto-generated docstring."""
                self.type = t
                self.text = text

        class MockResponse:
            """Auto-generated docstring."""

            def __init__(self, content_text):
                """Auto-generated docstring."""
                self.content = [MockBlock("text", text=content_text)]
                self.usage = type("obj", (object,), {"input_tokens": 10, "output_tokens": 10})()

        agent.gatekeeper.execute.return_value = MockResponse(raw_text)

        text_content, _, _ = agent.call_api(messages=[], tools=[])

        assert text_content == expected

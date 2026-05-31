import re

from debate.ipc.message import Evidence


class ApiMixin:
    """Mixin providing LLM API calling capabilities for agents."""

    def call_api(
        self, messages: list, tools: list, *, _retry: bool = False,
    ) -> tuple[str, list[Evidence], dict]:
        """Call the LLM API through the gatekeeper."""
        tools = tools or []

        # 1. Replace the fake tool with Anthropic's server-side tool
        has_web_search = any(t.get("name") == "web_search" for t in tools)
        if not has_web_search:
            tools.append({
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 3
            })

        def do_api_call():
            client = self._get_client()
            if client:
                return client.messages.create(
                    model=self.config.get("model", "claude-sonnet-4-20250514"),
                    max_tokens=2000,
                    system=self.get_system_prompt(),
                    messages=messages,
                    tools=tools,
                )
            # Default mock behaviour if no client is configured
            class MockBlock:
                def __init__(self, t, text="Mock response"):
                    self.type = t
                    self.text = text

            class MockResponse:
                def __init__(self):
                    self.content = [MockBlock("text", text="Mock response")]
                    self.usage = type("obj", (object,), {"input_tokens": 10, "output_tokens": 10})()
            return MockResponse()

        # 2. Make ONE call - no manual tool loop required
        response = self.gatekeeper.execute(do_api_call)

        usage_dict = {"input_tokens": 0, "output_tokens": 0}
        if hasattr(response, "usage"):
            usage_dict["input_tokens"] = response.usage.input_tokens
            usage_dict["output_tokens"] = response.usage.output_tokens
            self.log_api_call(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                cost_usd=0.0,
            )

        text_content = ""
        evidence_list: list[Evidence] = []

        # 3. Extract text and real citations from the response blocks
        if hasattr(response, "content"):
            for block in response.content:
                # Handle both dictionaries and SDK objects robustly
                is_dict = isinstance(block, dict)
                block_type = block.get("type", "") if is_dict else getattr(block, "type", "")

                if block_type == "text":
                    text_content += block.get("text", "") if is_dict else getattr(block, "text", "")

                elif block_type == "web_search_tool_result":
                    results = block.get("results", []) if is_dict else getattr(block, "results", [])
                    for res in results:
                        url = res.get("url", "unknown") if isinstance(res, dict) else getattr(res, "url", "unknown")
                        title = res.get("title", "No Title") if isinstance(res, dict) else getattr(res, "title", "No Title")
                        snippet = res.get("snippet", "") if isinstance(res, dict) else getattr(res, "snippet", "")

                        if url and url != "unknown":
                            evidence_list.append(Evidence(
                                url=url,
                                title=title,
                                snippet=snippet,
                                retrieved_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc)
                            ))

                elif block_type == "citation":
                    url = block.get("url", "unknown") if is_dict else getattr(block, "url", "unknown")
                    if url and url != "unknown":
                        title = block.get("title", "Cited Source") if is_dict else getattr(block, "title", "Cited Source")
                        snippet = block.get("snippet", "") if is_dict else getattr(block, "snippet", "")
                        if not snippet:
                            snippet = block.get("text", "") if is_dict else getattr(block, "text", "")

                        evidence_list.append(Evidence(
                            url=url,
                            title=title,
                            snippet=snippet,
                            retrieved_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc)
                        ))

        text_content = text_content.strip()

        # Clean up leading search announcements and thoughts
        search_phrases = [
            r"let me search", r"i need to search", r"let me gather",
            r"i'll search", r"i will search", r"let's search",
            r"i have the ammunition", r"i have the evidence", 
            r"now i have", r"now let me", r"excellent\.",
            r"arm myself with evidence"
        ]
        
        # Pattern to match a leading sentence containing any of the search phrases
        pattern = re.compile(r'^[^.!?\n]*(?:' + '|'.join(search_phrases) + r')[^.!?\n]*[.!?\n]+\s*', re.IGNORECASE)
        
        while True:
            # Strip leading dashes and whitespace
            text_content = re.sub(r'^(?:-+\s*|\s+)+', '', text_content)
            
            # Remove a leading sentence if it matches the pattern
            new_text = pattern.sub('', text_content)
            if new_text == text_content:
                break
            text_content = new_text
            
        # Final cleanup of any lingering dashes/whitespace just in case
        text_content = re.sub(r'^(?:-+\s*|\s+)+', '', text_content).strip()

        return text_content, evidence_list, usage_dict

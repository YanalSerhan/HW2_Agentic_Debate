import os
import re


class RAGRetriever:
    def __init__(self, data_path: str = "data/"):
        self.data_path = data_path
        self._cache = {}

    def load_knowledge_base(self, persona: str) -> str:
        if persona in self._cache:
            return self._cache[persona]

        file_path = os.path.join(self.data_path, f"{persona}.md")
        if not os.path.exists(file_path):
            return ""

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        self._cache[persona] = content
        return content

    def retrieve(self, persona: str, topic: str, round_number: int) -> str:
        kb_content = self.load_knowledge_base(persona)
        if not kb_content:
            return ""

        # Split into chunks, typically by paragraphs or list items
        chunks = [c.strip() for c in re.split(r'\n\n|\n(?=\d+\.)', kb_content) if c.strip()]

        # Simple keyword extraction from topic
        keywords = [word.lower() for word in re.findall(r'\b\w+\b', topic) if len(word) > 3]

        # Score chunks based on keyword matches
        scored_chunks = []
        for chunk in chunks:
            chunk_lower = chunk.lower()
            score = sum(1 for kw in keywords if kw in chunk_lower)
            # Add a slight bias to longer chunks which might contain more context
            score += len(chunk) / 1000.0
            scored_chunks.append((score, chunk))

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        # Get top 1 chunk
        top_chunks = [chunk for score, chunk in scored_chunks[:1]]

        return "\n\n".join(top_chunks)

    def get_context_for_argument(self, persona: str, topic: str, round_number: int) -> str:
        chunks = self.retrieve(persona, topic, round_number)
        if not chunks:
            return ""

        return f"RELEVANT CONTEXT FROM YOUR KNOWN POSITIONS AND STYLE:\n{chunks}\n"

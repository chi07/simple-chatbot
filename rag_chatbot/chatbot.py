from __future__ import annotations

from rag_chatbot.config import Settings
from rag_chatbot.embeddings import OpenAIEmbeddingClient
from rag_chatbot.llm import OpenAIChatClient
from rag_chatbot.qdrant_store import QdrantStore, SearchResult


class RagChatbot:
    def __init__(
        self,
        settings: Settings,
        embedding_client: OpenAIEmbeddingClient | None = None,
        qdrant_store: QdrantStore | None = None,
        chat_client: OpenAIChatClient | None = None,
    ):
        self.settings = settings
        self.embedding_client = embedding_client or OpenAIEmbeddingClient(settings)
        self.qdrant_store = qdrant_store or QdrantStore(settings)
        self.chat_client = chat_client or OpenAIChatClient(settings)

    def chat(self, question: str) -> dict:
        vector = self.embedding_client.embed(question)
        results = self.qdrant_store.search(vector, limit=self.settings.top_k)
        filtered_results = [
            result for result in results if result.score >= self.settings.min_score
        ]

        context = build_context(filtered_results, self.settings.max_context_chars)
        if not context:
            return {
                "answer": "I could not find relevant information in the documents.",
                "sources": [],
            }

        answer = self.chat_client.answer(context=context, question=question)
        return {
            "answer": answer,
            "sources": [
                {
                    "id": result.id,
                    "source": result.source,
                    "title": result.title,
                    "section": result.section,
                    "score": result.score,
                }
                for result in filtered_results
            ],
        }


def build_context(results: list[SearchResult], max_chars: int) -> str:
    sections: list[str] = []
    current_size = 0
    for index, result in enumerate(results, start=1):
        section = (
            f"[Source {index}]\n"
            f"Title: {result.title}\n"
            f"Source: {result.source}\n"
            f"Section: {result.section}\n"
            f"Score: {result.score:.4f}\n"
            f"Content:\n{result.text}"
        )
        if current_size + len(section) > max_chars:
            break
        sections.append(section)
        current_size += len(section)
    return "\n\n---\n\n".join(sections)

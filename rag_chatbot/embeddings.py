from __future__ import annotations

from openai import OpenAI

from rag_chatbot.config import Settings


class OpenAIEmbeddingClient:
    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        self.model = settings.openai_embedding_model
        self.client = OpenAI(api_key=settings.openai_api_key)

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

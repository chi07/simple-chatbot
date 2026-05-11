from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from rag_chatbot.config import Settings
from rag_chatbot.documents import Chunk


@dataclass(frozen=True)
class SearchResult:
    id: str
    score: float
    text: str
    source: str
    title: str
    section: str


class QdrantStore:
    def __init__(self, settings: Settings):
        self.url = settings.qdrant_url.rstrip("/")
        self.collection = settings.qdrant_collection
        self.vector_size = settings.qdrant_vector_size
        self.client = httpx.Client(timeout=60.0)

    def ensure_collection(self) -> None:
        response = self.client.get(f"{self.url}/collections/{self.collection}")
        if response.status_code == 200:
            return
        if response.status_code != 404:
            response.raise_for_status()

        payload = {
            "vectors": {
                "size": self.vector_size,
                "distance": "Cosine",
            }
        }
        create_response = self.client.put(
            f"{self.url}/collections/{self.collection}",
            json=payload,
        )
        create_response.raise_for_status()

    def upsert_chunks(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")

        points: list[dict[str, Any]] = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            points.append(
                {
                    "id": chunk.id,
                    "vector": vector,
                    "payload": {
                        "text": chunk.text,
                        "source": chunk.source,
                        "title": chunk.title,
                        "section": chunk.section,
                        "chunk_index": chunk.chunk_index,
                    },
                }
            )

        response = self.client.put(
            f"{self.url}/collections/{self.collection}/points",
            params={"wait": "true"},
            json={"points": points},
        )
        response.raise_for_status()

    def search(self, vector: list[float], limit: int) -> list[SearchResult]:
        payload = {
            "vector": vector,
            "limit": limit,
            "with_payload": True,
        }
        response = self.client.post(
            f"{self.url}/collections/{self.collection}/points/search",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        results: list[SearchResult] = []
        for item in data.get("result", []):
            point_payload = item.get("payload") or {}
            results.append(
                SearchResult(
                    id=str(item.get("id", "")),
                    score=float(item.get("score", 0.0)),
                    text=str(point_payload.get("text", "")),
                    source=str(point_payload.get("source", "")),
                    title=str(point_payload.get("title", "")),
                    section=str(point_payload.get("section", "")),
                )
            )
        return results

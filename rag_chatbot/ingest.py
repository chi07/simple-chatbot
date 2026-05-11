from __future__ import annotations

import argparse
from pathlib import Path

from rag_chatbot.config import get_settings
from rag_chatbot.documents import chunk_documents, load_documents
from rag_chatbot.embeddings import OpenAIEmbeddingClient
from rag_chatbot.qdrant_store import QdrantStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into Qdrant.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/docs"),
        help="Directory containing .txt, .md, .markdown, and .pdf files.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Number of chunks to embed/upsert per batch.",
    )
    args = parser.parse_args()

    settings = get_settings()
    documents = load_documents(args.data_dir)
    chunks = chunk_documents(
        documents,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    if not documents:
        raise SystemExit(f"No supported documents found in {args.data_dir}")
    if not chunks:
        raise SystemExit("No chunks were created from the documents")

    embedding_client = OpenAIEmbeddingClient(settings)
    qdrant_store = QdrantStore(settings)
    qdrant_store.ensure_collection()

    total_upserted = 0
    for start in range(0, len(chunks), args.batch_size):
        batch = chunks[start : start + args.batch_size]
        vectors = embedding_client.embed_batch([chunk.text for chunk in batch])
        qdrant_store.upsert_chunks(batch, vectors)
        total_upserted += len(batch)
        print(f"Upserted {total_upserted}/{len(chunks)} chunks")

    print("Ingestion completed")
    print(f"Documents: {len(documents)}")
    print(f"Chunks: {len(chunks)}")
    print(f"Collection: {settings.qdrant_collection}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf"}


@dataclass(frozen=True)
class Document:
    source: str
    title: str
    text: str


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    title: str
    section: str
    chunk_index: int


def load_documents(data_dir: Path) -> list[Document]:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

    documents: list[Document] = []
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = _read_file(path)
        if not text.strip():
            continue

        documents.append(
            Document(
                source=str(path),
                title=path.stem.replace("_", " ").replace("-", " ").strip(),
                text=text,
            )
        )

    return documents


def chunk_documents(
    documents: list[Document],
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[Chunk] = []
    for document in documents:
        words = document.text.split()
        start = 0
        chunk_index = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = " ".join(words[start:end]).strip()
            if chunk_text:
                chunk_id = _stable_chunk_id(document.source, chunk_index, chunk_text)
                chunks.append(
                    Chunk(
                        id=chunk_id,
                        text=chunk_text,
                        source=document.source,
                        title=document.title,
                        section=f"chunk-{chunk_index:04d}",
                        chunk_index=chunk_index,
                    )
                )

            if end == len(words):
                break

            start = end - chunk_overlap
            chunk_index += 1

    return chunks


def _read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"\n\n[Page {index}]\n{text}")
    return "\n".join(pages)


def _stable_chunk_id(source: str, chunk_index: int, text: str) -> str:
    raw_id = f"{source}:{chunk_index}:{text}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, raw_id))

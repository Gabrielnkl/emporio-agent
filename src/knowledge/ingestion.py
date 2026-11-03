"""Extract, chunk, embed, and index the store policy PDF into local Chroma."""

from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

from .vector_store import PROJECT_ROOT, get_policy_collection

POLICY_PDF = PROJECT_ROOT / "data" / "policies.pdf"
CHUNK_SIZE = 1400
CHUNK_OVERLAP = 200
EMBEDDING_BATCH_SIZE = 64


def chunk_page_text(text: str, page_number: int) -> list[tuple[str, dict[str, str | int]]]:
    """Split one PDF page into overlapping chunks with source-page metadata."""
    cleaned = re.sub(r"[ \t]+", " ", text.replace("\r", ""))
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    chunks = []
    start = 0
    index = 0
    while start < len(cleaned):
        end = min(start + CHUNK_SIZE, len(cleaned))
        if end < len(cleaned):
            boundary = max(cleaned.rfind("\n", start + CHUNK_SIZE // 2, end), cleaned.rfind(" ", start + CHUNK_SIZE // 2, end))
            if boundary > start:
                end = boundary
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append((chunk, {"source": POLICY_PDF.name, "page": page_number, "chunk": index}))
            index += 1
        if end >= len(cleaned):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


def _embed_chunks(client: OpenAI, documents: list[str], model: str) -> list[list[float]]:
    embeddings: list[list[float]] = []
    for start in range(0, len(documents), EMBEDDING_BATCH_SIZE):
        batch = documents[start : start + EMBEDDING_BATCH_SIZE]
        result = client.embeddings.create(model=model, input=batch)
        embeddings.extend(item.embedding for item in sorted(result.data, key=lambda item: item.index))
    return embeddings


def ingest_policy() -> int:
    """Rebuild the local Chroma collection from the supplied policy PDF."""
    if not POLICY_PDF.is_file():
        raise FileNotFoundError(f"Policy PDF not found: {POLICY_PDF}")
    client = OpenAI()
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    reader = PdfReader(str(POLICY_PDF))
    records = [
        record
        for page_number, page in enumerate(reader.pages, start=1)
        for record in chunk_page_text(page.extract_text() or "", page_number)
    ]
    if not records:
        raise ValueError("No text could be extracted from the policy PDF.")

    documents = [text for text, _ in records]
    metadatas = [metadata for _, metadata in records]
    ids = [f"policy-page-{metadata['page']}-chunk-{metadata['chunk']}" for metadata in metadatas]
    embeddings = _embed_chunks(client, documents, model)

    collection = get_policy_collection()
    existing_ids = collection.get(where={"source": POLICY_PDF.name}, include=["metadatas"])["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    return len(documents)


def main() -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Defina OPENAI_API_KEY no ambiente ou no arquivo .env.")
    count = ingest_policy()
    print(f"Indexados {count} trechos de {POLICY_PDF.name} em {PROJECT_ROOT / 'data' / 'chroma'}.")


if __name__ == "__main__":
    main()

"""Local persistent Chroma collection for policy document chunks."""

from pathlib import Path

import chromadb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma"
COLLECTION_NAME = "emporio_store_policies"


def get_policy_collection():
    """Return the persistent collection used for policy retrieval."""
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=None,
    )

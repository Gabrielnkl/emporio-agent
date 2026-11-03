"""Retrieve policy chunks from local Chroma using OpenAI embeddings."""

import os

from openai import OpenAI

from .vector_store import get_policy_collection


def retrieve_policy(question: str, openai_client: OpenAI, n_results: int = 4) -> str:
    """Embed a policy question and return the most relevant PDF excerpts."""
    collection = get_policy_collection()
    count = collection.count()
    if count == 0:
        return "A base de políticas ainda não foi indexada. Execute `python -m src.knowledge.ingestion` para prepará-la."

    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_response = openai_client.embeddings.create(model=model, input=question)
    query_embedding = embedding_response.data[0].embedding
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, count),
        include=["documents", "metadatas", "distances"],
    )

    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]
    if not documents:
        return "Não encontrei trechos de política para essa pergunta."

    excerpts = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        source = metadata.get("source", "policies.pdf") if metadata else "policies.pdf"
        page = metadata.get("page", "?") if metadata else "?"
        excerpts.append(f"[Fonte: {source}, página {page}; distância {distance:.3f}]\n{document}")
    return "Trechos recuperados do manual de políticas. Baseie a resposta somente nestes trechos e informe a página quando ajudar:\n\n" + "\n\n".join(excerpts)

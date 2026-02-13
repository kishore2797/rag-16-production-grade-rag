#!/usr/bin/env python3
"""
RAG Tutorial 16 — Production-Grade RAG
Minimal example: multi-tenant vector store — separate collection per tenant.
Run: pip install -r requirements.txt && python example.py
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_collection(client, tenant_id: str, collection_name: str):
    """Per-tenant collection name so data is isolated."""
    name = f"tenant_{tenant_id}_{collection_name}"
    return client.get_or_create_collection(name)


def main():
    client = chromadb.Client(Settings(anonymized_telemetry=False))
    # Tenant A and B have separate collections
    coll_a = get_collection(client, "tenant_a", "docs")
    coll_b = get_collection(client, "tenant_b", "docs")
    coll_a.add(
        ids=["a1"],
        embeddings=model.encode(["Tenant A confidential document."]).tolist(),
        documents=["Tenant A confidential document."],
    )
    coll_b.add(
        ids=["b1"],
        embeddings=model.encode(["Tenant B internal memo."]).tolist(),
        documents=["Tenant B internal memo."],
    )
    # Query as tenant A: only sees A's data
    res_a = coll_a.query(
        query_embeddings=model.encode(["confidential"]).tolist(),
        n_results=1,
        include=["documents"],
    )
    res_b = coll_b.query(
        query_embeddings=model.encode(["confidential"]).tolist(),
        n_results=1,
        include=["documents"],
    )
    print("Tenant A query 'confidential':", res_a["documents"][0])
    print("Tenant B query 'confidential':", res_b["documents"][0])
    print("\n→ Production adds auth, rate limits, and pluggable backends (Pinecone, Qdrant, etc.).")


if __name__ == "__main__":
    main()

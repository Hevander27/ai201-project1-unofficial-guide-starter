"""
Milestone 4 - Part 1: Embed chunks and load them into ChromaDB.

Reads data/chunks.json, embeds every chunk with all-MiniLM-L6-v2, and stores
the vectors in a persistent ChromaDB collection along with each chunk's source
document and position (needed later for citation/attribution). Rebuilds the
collection from scratch each run so re-embedding is idempotent.

Run from the project root:
    source .venv-1/bin/activate
    python src/embed.py
"""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_PATH = ROOT / "data" / "chunks.json"
CHROMA_PATH = ROOT / "data" / "chroma_db"

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION = "study_chunks"


def main() -> None:
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_PATH.name}")

    # Embed all chunk texts in one batch. all-MiniLM-L6-v2 outputs 384-dim
    # vectors; normalizing is harmless and keeps vectors unit-length.
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(
        [c["text"] for c in chunks],
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
    ).tolist()

    # Persistent on-disk store. hnsw:space=cosine makes query distances cosine
    # distance (0 = identical, ~1 = unrelated) - the right metric for sentence
    # embeddings and what the Milestone 4 distance thresholds assume.
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)  # fresh rebuild
    collection = client.create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"}
    )

    collection.add(
        ids=[c["id"] for c in chunks],
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=[
            {
                "source": c["source"],
                "position": int(c["id"].split("::")[1]),
                "n_tokens": c["n_tokens"],
            }
            for c in chunks
        ],
    )

    print(f"Stored {collection.count()} vectors in ChromaDB collection "
          f"'{COLLECTION}' at {CHROMA_PATH}")


if __name__ == "__main__":
    main()

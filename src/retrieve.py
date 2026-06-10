"""
Milestone 4 - Part 2: Retrieval.

retrieve_top_k(query, k) embeds the query with all-MiniLM-L6-v2 and returns the
k nearest chunks from ChromaDB, each with its source, position, and cosine
distance (0 = identical, higher = less related). Run directly to test retrieval
against the 5 evaluation questions from planning.md and print distance scores.

Run from the project root:
    source .venv-1/bin/activate
    python src/retrieve.py
"""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
CHROMA_PATH = ROOT / "data" / "chroma_db"

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION = "study_chunks"
DEFAULT_K = 6  # tuned up from 5: k=6 is needed to surface the 2357-method chunk

# Evaluation questions from planning.md (Evaluation Plan).
EVAL_QUERIES = [
    "What is pseudo-work and why does it hurt academic performance?",
    "How does active recall compare to re-reading for exam performance?",
    "What is the 2357 spaced repetition method and how do I use it?",
    "How does the Pomodoro Technique help students manage study time?",
    "What does the Feynman Technique involve and when should I use it?",
]

# Loaded once, lazily, and reused across calls.
_model = None
_collection = None


def _load():
    global _model, _collection
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        _collection = client.get_collection(COLLECTION)
    return _model, _collection


def retrieve_top_k(query: str, k: int = DEFAULT_K) -> list[dict]:
    """Return the k chunks nearest to `query`, sorted by ascending distance."""
    model, collection = _load()
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()
    res = collection.query(query_embeddings=query_embedding, n_results=k)
    return [
        {
            "text": doc,
            "source": meta["source"],
            "position": meta["position"],
            "distance": dist,
        }
        for doc, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        )
    ]


def _test() -> None:
    for query in EVAL_QUERIES:
        print("\n" + "=" * 78)
        print(f"QUERY: {query}")
        print("=" * 78)
        for i, r in enumerate(retrieve_top_k(query), 1):
            flag = "  <-- weak (>0.5)" if r["distance"] > 0.5 else ""
            print(f"\n[{i}] distance={r['distance']:.3f}  source={r['source']}"
                  f"  (chunk {r['position']}){flag}")
            print("    " + r["text"][:280].replace("\n", " ") + "...")


if __name__ == "__main__":
    _test()

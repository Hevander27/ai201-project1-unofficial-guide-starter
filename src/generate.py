"""
Milestone 5 - Part 1: Grounded generation.

ask(question) retrieves the top-k chunks (Milestone 4), builds a context-only
prompt, and calls Groq's llama-3.3-70b-versatile to answer using ONLY that
context. Source attribution is computed programmatically from the retrieved
chunks - not left to the model to add. Returns {answer, sources, chunks}.

Requires a Groq API key in .env (GROQ_API_KEY=...). Get a free one at
https://console.groq.com.

Run from the project root:
    source .venv-1/bin/activate
    python src/generate.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve_top_k

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

MODEL = "llama-3.3-70b-versatile"
DECLINE = "I don't have enough information on that."

# Grounding is ENFORCED here, not suggested: the model is told to use only the
# context, and to emit the exact DECLINE string when the context is insufficient.
SYSTEM_PROMPT = (
    "You are a study-skills Q&A assistant. Answer the user's question using "
    "ONLY the information in the numbered context passages provided. Rules:\n"
    "1. Use only facts stated in the context. Do NOT use prior knowledge or "
    "fill gaps with outside/general information.\n"
    f"2. If the context does not contain enough information to answer the "
    f"question, reply with exactly this sentence and nothing else: {DECLINE}\n"
    "3. Be concise, and keep every claim traceable to the passages."
)

_client = None


def _client_or_raise() -> Groq:
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key or key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY not set. Copy .env.example to .env and add your "
                "Groq key (free at https://console.groq.com)."
            )
        _client = Groq(api_key=key)
    return _client


def ask(question: str, k: int = 6) -> dict:
    """Retrieve context, generate a grounded answer, attach sources."""
    chunks = retrieve_top_k(question, k=k)
    context = "\n\n".join(
        f"[{i}] (source: {c['source']})\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    )
    user_msg = f"Context passages:\n\n{context}\n\nQuestion: {question}"

    resp = _client_or_raise().chat.completions.create(
        model=MODEL,
        temperature=0,  # deterministic, grounded - no creative drift
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    answer = resp.choices[0].message.content.strip()

    # Programmatic attribution: the unique source documents behind the context.
    # Suppressed when the model declines, since nothing was actually drawn from.
    declined = DECLINE.rstrip(".").lower() in answer.lower()
    sources = [] if declined else list(dict.fromkeys(c["source"] for c in chunks))
    return {"answer": answer, "sources": sources, "chunks": chunks}


def _test() -> None:
    queries = [
        "What is pseudo-work and why does it hurt academic performance?",
        "How does active recall compare to re-reading for exam performance?",
        "How does the Pomodoro Technique help students manage study time?",
        "How do I change a flat tire on my car?",  # out-of-corpus -> must decline
    ]
    for q in queries:
        print("\n" + "=" * 78)
        print("Q:", q)
        r = ask(q)
        print("\nANSWER:", r["answer"])
        print("SOURCES:", ", ".join(r["sources"]) if r["sources"] else "(none)")


if __name__ == "__main__":
    _test()

"""
Milestone 3 - Part 2: Chunk the cleaned documents.

Reads data/clean/*.txt, splits each document into chunks of at most 250 tokens
with ~45 tokens of overlap, measured with the all-MiniLM-L6-v2 tokenizer (the
same tokenizer the embedder uses, so the 250 cap means what we think it means).
Each chunk carries its source filename. Writes data/chunks.json and prints the
total count plus 5 random chunks for the Milestone 3 checkpoint.

Run from the project root:
    source .venv-1/bin/activate
    python src/chunk.py
"""

import json
import random
import re
from pathlib import Path

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "data" / "clean"
CHUNKS_PATH = ROOT / "data" / "chunks.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MAX_TOKENS = 250       # hard cap, comfortably under the model's 256-token limit
OVERLAP_TOKENS = 45    # context carried from one chunk into the next

# Loading only the tokenizer (not the full model) keeps chunking fast - we just
# need to count tokens the way the embedder will.
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


def n_tokens(text: str) -> int:
    """Token count excluding [CLS]/[SEP]; the model adds 2 specials at embed time."""
    return len(tokenizer.encode(text, add_special_tokens=False))


def split_sentences(text: str) -> list[str]:
    """Split into sentences so chunks break on natural boundaries, not mid-word.

    Breaks after . ! ? followed by whitespace, and on newlines (so list items
    and headings stay separate). Good enough for prose articles; we don't need
    linguistic perfection, just sane boundaries to pack from.
    """
    pieces = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in pieces if p.strip()]


def chunk_document(text: str) -> list[str]:
    """Greedily pack sentences into <=MAX_TOKENS chunks with OVERLAP_TOKENS overlap."""
    sentences = split_sentences(text)
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for sent in sentences:
        st = n_tokens(sent)

        # A single sentence longer than the cap can't fit - hard-split by tokens.
        if st > MAX_TOKENS:
            if current:
                chunks.append(" ".join(current))
                current, current_tokens = [], 0
            chunks.extend(_hard_split(sent))
            continue

        # Adding this sentence would overflow: close the chunk and start a new
        # one seeded with the overlapping tail of the one we just closed.
        if current_tokens + st > MAX_TOKENS:
            chunks.append(" ".join(current))
            current, current_tokens = _overlap_tail(current)

        current.append(sent)
        current_tokens += st

    if current:
        chunks.append(" ".join(current))
    return chunks


def _overlap_tail(sentences: list[str]) -> tuple[list[str], int]:
    """Trailing whole sentences whose combined length is <= OVERLAP_TOKENS."""
    tail: list[str] = []
    total = 0
    for sent in reversed(sentences):
        st = n_tokens(sent)
        if total + st > OVERLAP_TOKENS:
            break
        tail.insert(0, sent)
        total += st
    return tail, total


def _hard_split(sentence: str) -> list[str]:
    """Split an over-long sentence into <=MAX_TOKENS windows (with overlap)."""
    ids = tokenizer.encode(sentence, add_special_tokens=False)
    step = MAX_TOKENS - OVERLAP_TOKENS
    pieces = []
    for start in range(0, len(ids), step):
        pieces.append(tokenizer.decode(ids[start:start + MAX_TOKENS]))
        if start + MAX_TOKENS >= len(ids):
            break
    return pieces


def is_reference(text: str) -> bool:
    """True for bibliography/citation-dump chunks (from the academic PDFs).

    These can never answer a study-skills query but rank highly on topical
    keywords, crowding out real content. A chunk with 4+ numbered citations
    ([1], [2], ...) or 4+ URLs/DOIs is a reference list, not prose.
    """
    urls = len(re.findall(r"https?://|doi\.org", text))
    cites = len(re.findall(r"\[\d+\]", text))
    return cites >= 4 or urls >= 4


def main() -> None:
    files = sorted(CLEAN_DIR.glob("*.txt"))
    if not files:
        print("No cleaned files in data/clean/ - run src/ingest.py first.")
        return

    all_chunks = []
    per_doc = []
    dropped = 0
    for path in files:
        doc_chunks = chunk_document(path.read_text(encoding="utf-8"))
        kept = [ch for ch in doc_chunks if not is_reference(ch)]
        dropped += len(doc_chunks) - len(kept)
        for i, ch in enumerate(kept):
            all_chunks.append({
                "id": f"{path.stem}::{i}",
                "source": path.stem,
                "text": ch,
                "n_tokens": n_tokens(ch),
            })
        per_doc.append((path.stem, len(kept)))

    CHUNKS_PATH.write_text(
        json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # --- report -----------------------------------------------------------
    total = len(all_chunks)
    print(f"\nWrote {total} chunks -> {CHUNKS_PATH} "
          f"(dropped {dropped} reference/bibliography chunks)\n")
    print(f"{'document':45} {'chunks':>7}")
    print("-" * 54)
    for name, count in per_doc:
        print(f"{name[:44]:45} {count:>7}")
    print("-" * 54)
    print(f"{'TOTAL':45} {total:>7}")

    counts = [c["n_tokens"] for c in all_chunks]
    print(f"\ntokens/chunk: min={min(counts)} max={max(counts)} "
          f"avg={sum(counts) // total}")
    if total < 50:
        print("WARNING: <50 chunks - chunks may be too large.")
    elif total > 2000:
        print("WARNING: >2000 chunks - chunks may be too small.")

    # --- checkpoint: 5 random chunks --------------------------------------
    print("\n" + "=" * 70)
    print("5 RANDOM CHUNKS - read each: self-contained? a complete thought?")
    print("=" * 70)
    rng = random.Random(42)  # fixed seed -> reproducible sample
    for c in rng.sample(all_chunks, min(5, total)):
        print(f"\n--- {c['id']}  ({c['n_tokens']} tokens) ---")
        print(c["text"])


if __name__ == "__main__":
    main()

# The Unofficial Guide — Project 1

A retrieval-augmented (RAG) question-answering system over study-skills knowledge:
ingest documents → chunk → embed into ChromaDB → retrieve → generate a grounded
answer with Groq. Run the interface with `python app.py` (see the bottom of this file).

---

[![Watch Demo](https://i.imgur.com/yourThumbnailID.jpg)](https://imgur.com/a/tRIZoZx)

## Domain

**How to Become a Straight-A Student — study techniques, time management, and academic performance.**

Students trying to improve their grades get generic, often conflicting advice from
official channels (syllabi, tutoring centers, university websites). The genuinely
actionable knowledge — specific techniques like active recall, spaced repetition,
the Pomodoro method, the Feynman technique, and avoiding "pseudo-work" — is scattered
across a book, blogs, and research papers rather than consolidated anywhere. A RAG
system over these sources surfaces specific, evidence-backed answers that a generic
advising page never would.

---

## Document Sources

12 documents (8 `.txt` articles/excerpts, 4 PDFs including one book) covering study
techniques, time management, and the research behind them.

| # | Source | Type | File |
|---|--------|------|------|
| 1 | *How to Become a Straight-A Student* — Cal Newport | Book (PDF) | `data/documents/[Cal_Newport]_How_to_Become_a_Straight-A_Student__(z-lib.org).pdf` |
| 2 | Exam Study Expert — 51 Proven Study Tips | Blog (txt) | `data/documents/51 PROVEN Study Tips For Students.txt` |
| 3 | Kortext — 10 time-management strategies | Blog (txt) | `data/documents/timemangementsuccess.txt` |
| 4 | Queen's Online School — 8 time-management techniques | Blog (txt) | `data/documents/eighttimemanagementtips.txt` |
| 5 | XMind — Top 5 learning strategies | Blog (txt) | `data/documents/fivelearningstrategies.txt` |
| 6 | Active recall — overview | Blog (txt) | `data/documents/activerecall.txt` |
| 7 | BCU — Spaced repetition & the 2357 method | Blog (txt) | `data/documents/spacedrepetition-2357.txt` |
| 8 | Active recall vs. passive reading | Blog (txt) | `data/documents/activereading.txt` |
| 9 | Active recall — the cognitive science | Blog (txt) | `data/documents/activerecallscience.txt` |
| 10 | Cal Newport — "Pseudo-work does not equal work" | Blog excerpt (txt) | `data/documents/pseudowork.txt` |
| 11 | Enhancing Effective Strategies for Student Success | Research paper (PDF) | `data/documents/Enhancing Effective Strategies for Student Success.pdf` |
| 12 | Influence of Study Attitudes & Habits on Academic Performance (Tus) | Research paper (PDF) | `data/documents/IJARW1382.pdf` |

> Source URLs are listed in `planning.md` (Documents section).

---

## Chunking Strategy

**Chunk size:** 250 tokens (hard cap)
**Overlap:** 45 tokens
**Token counter:** the `all-MiniLM-L6-v2` tokenizer itself (not tiktoken or word count)
**Final chunk count:** **526** chunks across 12 documents

**Why these choices fit the documents:**
The 250-token cap exists because `all-MiniLM-L6-v2` silently truncates any input
beyond 256 tokens before embedding — a larger chunk would lose its tail at embed
time, so retrieval would ignore half of it. Counting with the model's own tokenizer
guarantees the 250 number means exactly what the embedder sees. The corpus is
paragraph-structured study-skills prose with roughly one technique per paragraph, so
~250 tokens maps to one self-contained technique-plus-explanation — the granularity a
query like "what is active recall?" should match. The 45-token overlap guards against
a technique straddling a chunk boundary.

**Preprocessing before chunking (`src/ingest.py`):**
- Loaded `.txt` with `utf-8-sig` (strips BOM) and PDFs with pdfplumber.
- Cleaned: unescaped HTML entities, stripped stray tags, normalized smart quotes/dashes
  to ASCII, collapsed whitespace.
- PDFs: lowered `x_tolerance` to fix lost word spacing, dropped page numbers and lines
  repeating across pages (headers/footers), and **reconstructed two-column pages
  row-by-row** so the left/right columns weren't interleaved into scrambled text.
- Chunking is sentence-aware, and **bibliography/citation-dump chunks were filtered out**
  (11 dropped) — they can't answer a study question but rank highly on keywords.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` (via `sentence-transformers`), 384-dimensional vectors,
stored in a persistent **ChromaDB** collection with cosine distance.

**Production tradeoff reflection:**
`all-MiniLM-L6-v2` fits this corpus well: the documents are short-to-medium study-skills
articles and academic papers in standard English, the model handles that register
effectively, and it runs locally with no API cost — useful for a corpus that gets
re-indexed as new guides are added. Semantic search bridges the vocabulary mismatch
between sources — "active recall," "retrieval practice," and "self-quizzing" map to
nearby vectors despite sharing no exact words. If cost were no constraint, a larger
model like `text-embedding-3-large` or `voyage-large-2` would give better accuracy on
the denser academic PDFs and a longer context window — which would also relax the
256-token truncation that currently caps chunk size; a multilingual model such as
`multilingual-e5-large` would let non-native-English students query in their first language.

---

## Grounded Generation

**System prompt grounding instruction** (`src/generate.py`):
The model is told to answer using **only** the numbered context passages, with these rules:

1. *"Use only facts stated in the context. Do NOT use prior knowledge or fill gaps with
   outside/general information."*
2. *"If the context does not contain enough information to answer the question, reply with
   exactly this sentence and nothing else: I don't have enough information on that."*
3. *"Be concise, and keep every claim traceable to the passages."*

Generation uses Groq `llama-3.3-70b-versatile` at **temperature 0** for deterministic,
grounded output. Retrieved chunks are injected as numbered blocks, each labeled with its
source document.

**How source attribution is surfaced:**
Attribution is **programmatic, not left to the model**. `ask()` returns the unique source
filenames behind the retrieved chunks in `result["sources"]`, which the UI shows in a
"Retrieved from" panel. When the model declines (insufficient context), the source list is
suppressed — nothing was drawn from, so nothing is cited.

---

## Evaluation Report

All five questions were run end-to-end through `src/generate.py`.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is pseudo-work and why does it hurt academic performance? | Studying with low focus for long hours without retaining much; intensity × time = work done | "Spending time studying but not accomplishing much due to lack of focus… low intensity of focus." Sources: Newport book, pseudowork | Relevant (top 0.32) | Accurate |
| 2 | How does active recall compare to re-reading for exam performance? | Active recall beats re-reading; ~23% higher scores; re-reading builds false familiarity | "Students using active recall score 15–25% higher… re-reading is 50% less effective." Sources: activereading, activerecallscience | Relevant (top 0.22) | Accurate (cites the 15–25% / 50% figures from the corpus rather than the 23% stat — both are present) |
| 3 | What is the 2357 spaced repetition method and how do I use it? | Review at increasing intervals after learning, using active recall each time | "Schedules reviews at Days 2, 5, 10, 17 after learning; work backward from the exam date." Sources: spacedrepetition-2357, … | Partially relevant (top result 0.45 was *generic* spaced-repetition; the 2357 chunk ranked 6th) | Accurate (and faithful to the source's Day-2/5/10/17 interpretation) |
| 4 | How does the Pomodoro Technique help students manage study time? | 25-min focused intervals + short breaks; prevents burnout, trains focus | "25-minute work intervals with brief breaks; improves focus and prevents burnout." Sources: fivelearningstrategies, eighttimemanagementtips, IJARW1382 | Relevant (top 0.24) | Accurate |
| 5 | What does the Feynman Technique involve and when should I use it? | Explain a concept simply as if teaching it; gaps reveal gaps in understanding | "Explaining a concept out loud as if teaching a beginner; combines active recall with elaboration." Sources: fivelearningstrategies, activerecall, … | Relevant (top 0.39) | Accurate |

**Out-of-corpus control:** asked "How do I change a flat tire on my car?" → the system
returned *"I don't have enough information on that."* with no sources, instead of inventing
an answer. Grounding holds.

**Retrieval quality:** Relevant (4/5) / Partially relevant (Q3)
**Response accuracy:** Accurate (5/5)

---

## Failure Case Analysis

**Question that failed:** Q3 — "What is the 2357 spaced repetition method and how do I use it?"
(a *retrieval-ranking* failure that generation happened to recover from).

**What the system returned:** The end-to-end answer was actually correct, but the **retrieval
ranking was wrong**: the top result (distance 0.45) was a *generic* passage about spaced
repetition, and an academic page-header chunk ranked #2. The chunk that actually defines the
2357 schedule ranked **6th** (distance 0.575), and the most detailed schedule chunk didn't
appear in the top 15 at all.

**Root cause (embedding stage):** The 2357 schedule is **list-formatted** — "Day 0: Learn…
Day 2: First review… Day 5…". That's mostly short fragments and numbers, which
`all-MiniLM-L6-v2` embeds poorly against a natural-language question, so generic prose *about*
spaced repetition out-ranks the specific answer. The answer only made it into the model's
context because `k` was tuned up to 6 (the schedule chunk sits at rank 6); at `k=4` this query
would have failed end-to-end.

**What I would change to fix it:** Add **hybrid retrieval** (combine vector similarity with a
keyword/BM25 match on terms like "2357"), or store a short prose summary alongside list-heavy
content so the schedule has a sentence-shaped representation to match against. Both give
list-formatted, fact-dense content a fair chance of ranking in the top results.

---

## Spec Reflection

**One way the spec helped during implementation:**
The Chunking Strategy section forced me to commit to a concrete token count *before* coding,
and pinning it to the embedding model's tokenizer is what surfaced the 256-token truncation
limit — I would otherwise have chunked at 400–500 tokens and silently lost half of every
chunk at embed time. The architecture diagram also gave each pipeline stage a clear tool
target, so each milestone was a matter of implementing one labeled box.

**One way the implementation diverged from the spec, and why:**
The original plan specified FAISS for the vector store, the Anthropic API for generation, and
live scraping (requests/BeautifulSoup/PRAW) for ingestion. The implementation uses **ChromaDB**
(stores vectors + metadata together, matching the assignment and installed deps), **Groq**
(free-tier, the recommended default), and **local `.txt`/`.pdf` loading** instead of scraping
(the sources were JavaScript-rendered or bot-blocked, so manual collection was more reliable).
The domain itself also pivoted — from an earlier DACA-policy idea to study skills — because the
study-skills sources were far easier to collect cleanly.

---

## AI Usage

**Instance 1 — Two-column PDF reconstruction**
- *What I gave the AI:* the scrambled output chunks from the academic PDFs (e.g. "Effective
  study strategies are the most **umes of complex information**…") and the cleaning code.
- *What it produced:* a diagnosis (pdfplumber reads two-column pages straight across the gutter,
  interleaving columns) and a row-aware `_extract_page` that groups words into rows, treats
  full-width lines as headers, and reads each column separately.
- *What I changed/directed:* an earlier per-page "is it two-column?" guess failed on mixed
  pages (single-column abstract + two-column body); I directed it toward the row-based approach,
  which fixed the mixed intro page.

**Instance 2 — Diagnosing the evaluation gap**
- *What I gave the AI:* the Milestone-4 retrieval results, where Q1 (pseudo-work) and Q3 (2357)
  returned weak, off-topic chunks.
- *What it produced:* a grep showing `pseudo-work` and `2357` had **0 occurrences** in the
  corpus — the eval questions tested content I'd planned (the Newport book, the BCU page) but
  never actually ingested.
- *What I changed/directed:* I added the missing sources rather than rewriting the questions,
  then re-ran the pipeline; Q1 went from distance 0.61 to 0.32.

> Reflection sections above describe the actual build; adjust the wording to your own voice
> before submitting.

---

## Running the system

```bash
source .venv-1/bin/activate          # environment with all deps
# one-time / after changing documents:
python src/ingest.py                 # load + clean data/documents -> data/clean
python src/chunk.py                  # chunk -> data/chunks.json
python src/embed.py                  # embed -> ChromaDB (data/chroma_db)
# query:
python src/retrieve.py               # test retrieval (5 eval questions)
python src/generate.py               # test grounded generation
python app.py                        # Gradio UI at http://localhost:7860
```

Requires a free Groq API key in `.env` (`GROQ_API_KEY=…`; see `.env.example`).

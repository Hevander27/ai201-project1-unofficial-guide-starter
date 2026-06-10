# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
DACA (Deferred Action for Childhood Arrivals) — renewal timelines, legal status, and policy updates
This domain was chosen because DACA recipients face urgent, high-stakes decisions that official channels communicate poorly. USCIS.gov is vague about processing times, lags behind court developments, and doesn't capture real-world wait experiences. 
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->


+-----+----------------------------------------------------------+--------------------------------------------------+
| #   | Source                                                   | Description                                      |
+-----+----------------------------------------------------------+--------------------------------------------------+
| OFFICIAL / GOVERNMENT                                                                                             |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 1   | https://www.uscis.gov/i-821d                             | USCIS DACA page: renewal guidance, 80+ FAQ,      |
|     |                                                          | form instructions                                |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 2   | https://egov.uscis.gov/processing-times/                 | Live processing times by form and service center |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 3   | https://www.federalregister.gov                          | 2022 DACA Final Rule and subsequent rulemaking   |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 4   | whitehouse.gov/presidential-actions/2025/12/             | Dec 2025 executive order restricting foreign     |
|     | restricting-and-limiting-the-entry...                    | national entry; advance parole risk context      |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 5   | travel.state.gov/…/suspension-of-visa-issuance…          | State Dept. visa suspension; enforcement climate |
|     |                                                          | context for DACA holders                         |
+-----+----------------------------------------------------------+--------------------------------------------------+
| LEGAL & ADVOCACY                                                                                                  |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 6   | https://www.nilc.org/resources/latest-daca-developments/ | NILC court decision and injunction tracker       |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 7   | nilc.org/articles/why-some-daca-renewals-are-taking-     | NILC March 2026: delay causes and recipient      |
|     | longer-and-what-you-can-do/                              | action steps                                     |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 8   | https://www.ilrc.org/daca                                | ILRC toolbox: eligibility explainers, practice   |
|     |                                                          | alerts, policy memos through 2026                |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 9   | https://www.nwirp.org/daca/                              | NWIRP community advisories and renewal guidance  |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 10  | sglegalgroup.com/blog/new-uscis-enhanced-                | Expanded FBI background checks starting          |
|     | background-checks…                                       | April 27, 2026; impact on pending renewals       |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 11  | https://www.boundless.com/blog/daca-reddit-faqs          | Top 12 Reddit DACA questions answered by         |
|     |                                                          | immigration experts                              |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 12  | https://immigrantsrising.org                             | Step-by-step first-time and renewal guides       |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 13  | https://www.americanimmigrationcouncil.org               | DACA fact sheets and litigation history          |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 14  | https://www.fwd.us                                       | Policy explainers and Dreamer advocacy updates   |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 15  | https://www.aila.org                                     | Processing time tracking and attorney guidance   |
+-----+----------------------------------------------------------+--------------------------------------------------+
| REDDIT / COMMUNITY                                                                                                |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 16  | reddit.com/r/DACA/comments/1tzujv5/                      | Approval Mega Thread; best crowdsourced          |
|     | approval_mega_thread…                                    | filing-to-approval timeline data                 |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 17  | reddit.com/r/DACA/comments/1u0sn86/                      | Community thread documenting unusual DACA        |
|     | update_6_something_big_and_weird…                        | processing anomaly                               |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 18  | r/DACA (reddit.com/r/DACA)                               | Primary hub; users post filing dates, biometrics,|
|     |                                                          | and approval timelines                           |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 19  | r/immigration (reddit.com/r/immigration)                 | Personal renewal experiences and attorney        |
|     |                                                          | commentary                                       |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 20  | r/Dreamers (reddit.com/r/Dreamers)                       | Lived renewal experiences and practical advice   |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 21  | r/ImmigrationLaw (reddit.com/r/ImmigrationLaw)           | Procedural delays and escalation options         |
+-----+----------------------------------------------------------+--------------------------------------------------+
| 22  | r/AskImmigration (reddit.com/r/AskImmigration)           | Q&A format; individual-situation questions       |
+-----+----------------------------------------------------------+--------------------------------------------------+
---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size: 400-500 tokens**
**Overlap: 50–75 tokens**
**Reasoning:**
Reddit posts are short and self-contained — 400 tokens captures a complete timeline post without splitting it. The Approval Mega Thread should be parsed comment-by-comment since each comment is a discrete data point. Legal/advocacy documents (NILC, ILRC) are paragraph-structured; 400–500 tokens maps to one concept or ruling per chunk — smaller chunks would split court rulings mid-explanation. FAQ documents (USCIS, Boundless) should be chunked by Q&A pair where possible. Executive orders (#4, #5) warrant the full 75-token overlap since legal conditions often span paragraph transitions. The overlap generally guards against facts straddling boundaries — e.g., "processing times have increased significantly" followed by the actual numbers in the next sentence.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->


**Embedding model: all-MiniLM-L6-v2 via sentence-transformers**

**Top-k: 6**

**Production tradeoff reflection:**
all-MiniLM-L6-v2 fits this corpus well: documents are short-to-medium length, it handles informal and semi-formal English effectively, and it has no API cost — important for a corpus needing frequent re-indexing as court decisions and Reddit posts accumulate. At k=6, the LLM gets enough context to synthesize across source types (e.g., NILC legal update + Reddit timeline) without noise. Semantic search handles the vocabulary mismatch between formal legal language and Reddit slang — both map to similar vectors when the underlying meaning is shared. If cost were no constraint, text-embedding-3-large or voyage-large-2 would offer better accuracy on dense legal text and longer context windows; multilingual-e5-large would support Spanish-language queries from bilingual recipients.


---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

+---+------------------------------------------------+---------------------------------------------------------------------------------+
| # | Question                                       | Expected answer                                                                 |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
| 1 | How long are DACA renewals taking in 2026?     | 6–12+ months real-world per Reddit Mega Thread and NILC March 2026 article;     |
|   |                                                | congressional letters from March–April 2026 confirm recipients expiring while   |
|   |                                                | waiting                                                                         |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
| 2 | Can someone apply for DACA for the first time  | No — initial applications frozen since Judge Hanen's July 2021 order; USCIS    |
|   | right now?                                     | accepts the fee but does not adjudicate                                         |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
| 3 | What did the Fifth Circuit rule on DACA in     | Upheld APA violation finding; narrowed injunction to Texas only and to work     |
|   | January 2025?                                  | authorization, not deferred action itself                                       |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
| 4 | When should I submit my DACA renewal?          | 120–150 days before expiration per USCIS; Reddit community recommends the full  |
|   |                                                | 150 days given current delays                                                   |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
| 5 | How do the new USCIS background checks affect  | Expanded FBI checks starting April 27, 2026 may add review time to             |
|   | my pending renewal?                            | already-delayed pending cases                                                   |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

Anticipated Challenges

1. Outdated Reddit timelines. Posts from 2021–2023 showing 2–3 month waits will be retrieved alongside 2026 posts showing 10+ months. The Approval Mega Thread must be tagged at the comment level, not just the thread level. Mitigation: attach post_date metadata to every chunk and surface it in the generation prompt.

2. Vocabulary mismatch between legal and community sources. NILC's "work authorization component of the Fifth Circuit's narrowed injunction" and a Reddit post's "they can still take your EAD even if your DACA is fine" describe the same fact with zero shared vocabulary. Mitigation: ensure legal sources aren't drowned out by Reddit volume; consider source-type weighting in retrieval scoring.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->


┌──────────────────────────────────────────────────────┐
│                     USER QUERY                       │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  1. DOCUMENT INGESTION                               │
│  requests + BeautifulSoup, PRAW (Reddit)             │
│  Tag: source_url, source_type, date_scraped          │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  2. CHUNKING                                         │
│  tiktoken + custom chunk_text()                      │
│  400–500 tokens, 50–75 overlap                       │
│  Q&A split for FAQs; comment split for Mega Thread   │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  3. EMBEDDING + VECTOR STORE                         │
│  sentence-transformers (all-MiniLM-L6-v2) + FAISS   │
│  384-dim vectors; JSON sidecar for metadata          │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  4. RETRIEVAL                                        │
│  FAISS cosine similarity, retrieve_top_k(k=6)        │
│  Returns chunks with source URL + date metadata      │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  5. GENERATION                                       │
│  Anthropic API (claude-sonnet-4) + Gradio UI         │
│  Chunks injected as numbered context; answer cites   │
│  source and date-qualifies time-sensitive claims     │
└──────────────────────────────────────────────────────┘
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
Input to Claude: Documents list + Chunking Strategy section. Ask it to implement scrape_document(url, source_type) using requests/BeautifulSoup, ingest_reddit(url) using PRAW, and chunk_text(text, chunk_size=450, overlap=60, source_type=None) using tiktoken with Q&A boundary splitting for FAQ docs and comment-by-comment splitting for the Mega Thread. Verify by running one URL from each source type and inspecting that chunks are complete and correctly tagged.

**Milestone 4 — Embedding and retrieval:**
Input to Claude: Retrieval Approach section + chunk schema from Milestone 3. Ask it to implement embed_chunks() using sentence-transformers, build_index() storing vectors in FAISS with a JSON metadata sidecar, and retrieve_top_k(query, k=6). Verify by running the 5 evaluation questions and checking that at least 4 of 6 returned chunks are topically relevant.

**Milestone 5 — Generation and interface:**
Input to Claude: Evaluation Plan table + retrieve_top_k output schema. Ask it to implement generate_answer(query, chunks) that injects chunks as numbered context blocks with source citation instructions, plus a Gradio UI with query input, answer display, and expandable Sources section. Verify by running all 5 evaluation questions end-to-end and checking answers match expected results with proper source attribution.
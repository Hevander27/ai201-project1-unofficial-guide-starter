# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
**How to Become a Straight-A Student — study techniques, time management, and academic performance**

This domain was chosen because students looking to improve their grades often get generic or conflicting advice from official academic channels (syllabi, tutoring centers, university websites). The most actionable knowledge — specific techniques like active recall, spaced repetition, the Pomodoro method, and pseudo-work avoidance — is scattered across blogs, research papers, and community forums rather than consolidated in one place. A RAG system over these sources can surface specific, evidence-backed answers that a university advising page simply wouldn't.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->


+-----+--------------------------------------------+--------------------------------------------------+
| #   | Source                                     | Description                                      |
+-----+--------------------------------------------+--------------------------------------------------+
| BOOK                                                                                                  |
+-----+--------------------------------------------+--------------------------------------------------+
| 1   | How to Become a Straight-A Student         | Cal Newport; core framework: pseudo-work,        |
|     | — Cal Newport (2006)                       | focus intensity, time management, and            |
|     |                                            | exam/paper strategies based on real student      |
|     |                                            | interviews                                       |
+-----+--------------------------------------------+--------------------------------------------------+
| BLOGS & ARTICLES                                                                                      |
+-----+--------------------------------------------+--------------------------------------------------+
| 2   | examstudyexpert.com/study-tips/            | 51 proven study tips: retrieval practice,        |
|     |                                            | spaced repetition, "eat the frog" technique,     |
|     |                                            | and scheduling guilt-free rest                   |
+-----+--------------------------------------------+--------------------------------------------------+
| 3   | kortext.com/student-hub/study-tips/        | 10 time management strategies for students:      |
|     | ten-effective-time-management-             | Pomodoro technique, goal-setting before          |
|     | strategies-for-successful-studying/        | sessions, and breaking tasks into smaller chunks |
+-----+--------------------------------------------+--------------------------------------------------+
| 4   | queensonlineschool.com/                    | 8 student-centered time management techniques:   |
|     | time-management-for-students/              | time blocking, Pomodoro, and the Eisenhower      |
|     |                                            | Matrix with practical examples                   |
+-----+--------------------------------------------+--------------------------------------------------+
| 5   | xmind.com/blog/best-study-techniques       | Top 5 learning strategies for 2025: active       |
|     |                                            | reading, the Feynman Technique, visualization,   |
|     |                                            | and long-term retention methods                  |
+-----+--------------------------------------------+--------------------------------------------------+
| 6   | bcu.ac.uk/exams-and-revision/              | Birmingham City University: what active recall   |
|     | best-ways-to-revise/active-recall          | is, how it strengthens neural connections, and   |
|     |                                            | how to combine it with spaced repetition         |
+-----+--------------------------------------------+--------------------------------------------------+
| 7   | bcu.ac.uk/exams-and-revision/              | Birmingham City University: spaced repetition    |
|     | best-ways-to-revise/spaced-repetition      | and the 2357 method — reviewing material at      |
|     |                                            | increasing intervals based on the forgetting     |
|     |                                            | curve                                            |
+-----+--------------------------------------------+--------------------------------------------------+
| 8   | 5staressays.com/blog/                      | Active recall vs. passive reading: 2024 study    |
|     | active-recall-vs-passive-reading           | of 500 college students found active recall      |
|     |                                            | led to 23% higher final exam scores              |
+-----+--------------------------------------------+--------------------------------------------------+
| PDFs                                                                                                  |
+-----+--------------------------------------------+--------------------------------------------------+
| 9   | hpe.researchcommons.org/cgi/viewcontent    | Peer-reviewed paper (2025): active recall and    |
|     | .cgi?article=1348&context=journal          | spaced repetition vs. traditional study methods; |
|     |                                            | also covers sleep and diet as academic           |
|     |                                            | performance factors                              |
+-----+--------------------------------------------+--------------------------------------------------+
| 10  | sciencedirect.com/science/article/abs/     | ScienceDirect study (2025): spaced repetition    |
|     | pii/S187712972500231X                      | and active recall among pharmacy students;       |
|     |                                            | evidence that retrieval-based learning           |
|     |                                            | outperforms passive review significantly         |
+-----+--------------------------------------------+--------------------------------------------------+
---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size: 400–500 tokens**

**Overlap: 50–75 tokens**

**Reasoning:**
Blog posts and articles (Exam Study Expert, Kortext, Queen's Online School) are paragraph-structured with one technique or concept per paragraph — 400–500 tokens maps naturally to one complete idea per chunk. Smaller chunks would split mid-explanation, e.g., a description of the Pomodoro method cut before the step-by-step instructions. Academic PDFs (ScienceDirect, Health Professions Education) are denser and more formal; the full 75-token overlap is warranted here since key findings often span paragraph transitions (e.g., a claim followed by its supporting data in the next paragraph). The book (Newport) should be chunked by section or subsection where possible, since each addresses a distinct strategy. The overlap generally guards against technique explanations straddling boundaries — e.g., "active recall strengthens memory" followed by the specific how-to steps in the next sentence.
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
| 1 | What is pseudo-work and why does it hurt       | Pseudo-work is studying in distracted, low-focus environments for long hours    |
|   | academic performance?                          | without retaining much; Cal Newport argues intensity of focus x time = actual   |
|   |                                                | work done, so long unfocused sessions produce less than short focused ones      |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
| 2 | How does active recall compare to re-reading   | A 2024 study of 500 college students found active recall led to 23% higher      |
|   | for exam performance?                          | final exam scores; re-reading creates false familiarity without strengthening   |
|   |                                                | memory retrieval pathways                                                       |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
| 3 | What is the 2357 spaced repetition method      | Review material the day after a lesson, 2 days later, 3 days later, then 7      |
|   | and how do I use it?                           | days later; each review should use active recall rather than passive re-reading |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
| 4 | How does the Pomodoro Technique help           | Work in 25-minute focused intervals followed by a 5-minute break; after 4       |
|   | students manage study time?                    | intervals take a 15–30 minute break; prevents burnout and trains sustained      |
|   |                                                | concentration                                                                   |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
| 5 | What does the Feynman Technique involve        | Explain a concept in simple terms as if teaching it to someone else; gaps in    |
|   | and when should I use it?                      | your explanation reveal gaps in understanding; best used after initial reading  |
|   |                                                | to confirm true comprehension vs surface familiarity                            |
+---+------------------------------------------------+---------------------------------------------------------------------------------+
---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->


1. **Conflicting advice across sources.** A blog post claiming "study more hours" directly contradicts Newport's pseudo-work argument that intensity matters more than time. The LLM may retrieve both and generate a muddled or contradictory answer. Mitigation: tag each chunk with source type (research-backed vs. general advice blog) and surface it in the prompt so the model can weight evidence-based sources more heavily.

2. **Technique names used inconsistently across sources.** "Active recall," "retrieval practice," and "self-quizzing" all describe the same method but share no exact vocabulary. A query about "self-testing" may miss chunks that only use "retrieval practice." Mitigation: during ingestion, add a short normalized tag (e.g., technique: active_recall) to relevant chunks so retrieval isn't purely dependent on surface wording matching.

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
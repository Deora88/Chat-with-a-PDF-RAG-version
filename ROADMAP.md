# Chat With a PDF — RAG Version — Roadmap

**Stack:** Python + Flask
**LLM (answering):** Groq API — model: `openai/gpt-oss-20b`
**Embeddings (retrieval):** `sentence-transformers` (local, free, no API key —
model: `all-MiniLM-L6-v2`)
**Vector store:** ChromaDB (local, file-based)
**Goal:** Upload a PDF → split into chunks → embed chunks → store in a vector
database → on each question, retrieve only the most relevant chunks → send
just those to the LLM.

This is v2 of the original no-RAG project. The original `chat-with-pdf/`
folder is untouched and kept as a comparison baseline.

---

## Why RAG, and what actually changed
In v1, every question sent the ENTIRE PDF text to the LLM. That broke on
large PDFs (hit Groq's 8,000 tokens/minute limit on a 28-page PDF during v1
testing) and wasted tokens on irrelevant content.

In v2, only the chunks relevant to the question are sent — found via
semantic similarity search, not keyword matching.

---

## Milestone 0 — Environment Setup ✅
- [x] New project folder, separate venv
- [x] Installed: flask, python-dotenv, pypdf, groq, chromadb, sentence-transformers
- [x] Reused the same GROQ_API_KEY from the v1 project
- [x] Confirmed server runs

## Milestone 1 — Project Skeleton ✅
- [x] `app.py` — Flask entrypoint
- [x] `/` route serving a response

## Milestone 2 — PDF Upload + Text Extraction ✅
- [x] `POST /upload`, pypdf extraction (same approach as v1)

## Milestone 3 — Chunking ✅
- [x] `chunking.py` — word-count based chunking with overlap
- [x] Verified standalone with `test_chunking.py` (1200 words -> 3 chunks:
      500 / 500 / 300, confirming overlap math)

## Milestone 4 — Embeddings + Vector Store ✅
- [x] Verified `sentence-transformers` standalone (`test_embeddings.py`) —
      confirmed semantically related sentences score higher similarity than
      unrelated ones
- [x] Verified ChromaDB standalone (`test_chromadb.py`) — confirmed
      retrieval correctly ranks relevant chunks above irrelevant ones

## Milestone 5 — Retrieval wired into real documents ✅
- [x] `/upload` now chunks, embeds, and stores every uploaded PDF in its own
      ChromaDB collection (keyed by document_id)

## Milestone 6 — RAG-Powered /ask Endpoint ✅
- [x] `/ask` embeds the question, retrieves top-4 relevant chunks, builds a
      prompt from ONLY those chunks, sends to Groq
- [x] Validated against v1's exact failure case: a 28-page PDF that broke v1
      worked cleanly in v2
- [x] Stress-tested with a 144-page academic paper (861,486 characters,
      287 chunks) — worked correctly, retrieved relevant sections for
      different questions

## Milestone 7 — Frontend ✅
- [x] Adapted v1's design (paper-stack aesthetic) for this project
- [x] Shows chunk count on upload
- [x] Shows "chunks used" per answer for retrieval transparency

## Milestone 8 — Polish / Compare ✅ (first pass)
- [x] Documented the 144-page test as the headline proof point
- [x] `PROJECT_SUMMARY.md` written for presentation

---

## TODO LATER
- Side-by-side comparison of v1 vs v2 answer quality on the SAME small PDFs
  (where RAG isn't strictly necessary) to see if/how answers differ.
- Experiment with chunk size, overlap, and top-k retrieval count.
- Try sentence/paragraph-aware chunking instead of raw word-count chunking.
- Persistent storage beyond ChromaDB's local files, for multi-user/deployment.

---

## Notes / Decisions Log
- Embeddings run LOCALLY via sentence-transformers, Groq does not offer an
  embeddings API, only chat completions. This is a deliberate two-provider
  setup: local embeddings + hosted LLM.
- Chose ChromaDB for its simplicity, no server to run, stores data as local
  files, good for a single-user learning project.
- Confirmed real-world result: a 28-page PDF that returned a hard 413 token-
  limit error in v1 was handled without issue in v2. A 144-page paper
  (861K characters) was also handled successfully, chunked into 287 pieces,
  with only ~4 chunks used per answer.

## Presentation Line
"Here's a 144-page research paper — 861,000 characters. My first version
couldn't even process a 28-page PDF without hitting a rate limit. This
version breaks it into 287 chunks, and when I ask a question, it retrieves
just the relevant ones — here's the proof, working live."

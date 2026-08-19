# Chat With a PDF — RAG Version — Project Summary

## What it is
A web app that lets a user upload a PDF and ask natural-language questions
about its contents. Unlike the first version of this project, this one uses
**Retrieval-Augmented Generation (RAG)**: instead of sending an entire
document to the LLM on every question, it breaks the document into chunks,
converts each chunk into a searchable vector (embedding), and — for every
question — retrieves only the handful of chunks most relevant to that
question before asking the LLM to answer.

This is v2 of a two-part project. v1 proved out the basic mechanics of an
LLM app (upload, extract, prompt, answer) without RAG, and hit a real,
concrete limitation: large PDFs exceeded the LLM provider's token limit.
v2 exists specifically to solve that.

## Tech stack
| Layer | Choice |
|---|---|
| Backend | Python + Flask |
| PDF text extraction | `pypdf` |
| Chunking | Custom function — word-count based, with overlap |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) — runs locally, free, no API key |
| Vector store | ChromaDB (local, file-based, one collection per document) |
| LLM (answering) | Groq API — model: `openai/gpt-oss-20b` |
| Frontend | Custom HTML/CSS/JavaScript (no framework) |

## How it works
1. **Upload** — User uploads a PDF via drag-and-drop or file picker.
2. **Extraction** — `pypdf` pulls raw text from every page.
3. **Chunking** — The full text is split into overlapping chunks
   (~500 words each, 50-word overlap) so no idea gets cut cleanly in half
   at a chunk boundary.
4. **Embedding** — Each chunk is converted into a 384-number vector using a
   local embedding model, capturing its semantic meaning.
5. **Storage** — Chunks and their embeddings are stored in a ChromaDB
   collection unique to that document (keyed by a generated `document_id`).
6. **Ask** — User asks a question. The question itself is embedded using the
   same model.
7. **Retrieval** — ChromaDB compares the question's embedding against every
   stored chunk and returns the top 4 most semantically similar ones.
8. **Generation** — Only those 4 chunks (not the whole document) are
   combined with the question into a prompt and sent to Groq's
   `openai/gpt-oss-20b` model.
9. **Answer** — The model's grounded answer is returned and displayed in a
   running chat thread, along with how many chunks were used.

```
[Browser] --PDF--> [/upload]
                       |
              pypdf extracts text
                       |
              split into overlapping chunks
                       |
              each chunk embedded (sentence-transformers)
                       |
              stored in ChromaDB (per-document collection)

[Browser] --question--> [/ask]
                       |
              question embedded
                       |
              ChromaDB returns top-4 similar chunks
                       |
              chunks + question --> Groq (gpt-oss-20b)
                       |
              answer --> [Browser]
```

## Proof it works: the 144-page test
The clearest demonstration of why this version exists: a 144-page academic
survey paper ("A Survey of Large Language Models," arXiv:2303.18223 —
861,486 characters) was uploaded and split into 287 chunks.

- **v1 (no RAG)** could not have handled this — it hit a hard token-limit
  error on a document roughly a fifth this size (a 28-page PDF, ~35,000
  characters) during earlier testing.
- **v2 (RAG)** processed the full 144-page document without issue, and
  correctly answered a specific technical question ("What are pre-trained
  language models?") by retrieving only the relevant chunks — not the
  other 283.

This is the core proof point: RAG doesn't just make large documents
possible, it makes answers more targeted, since the LLM only ever sees the
text that's actually relevant to the question asked.

## Key design decisions
- **Local embeddings, hosted LLM** — Groq does not offer an embeddings API,
  only chat completions. Embeddings run locally via `sentence-transformers`
  (free, no rate limit, no API key), while answer generation still uses
  Groq's fast hosted inference. This is a common real-world pattern: cheap
  local models for retrieval, a stronger hosted model for generation.
- **One ChromaDB collection per document** — keeps each document's chunks
  isolated, named using its `document_id`, so multiple documents can be
  uploaded without their chunks mixing.
- **Word-count chunking with overlap** — simple to reason about, and the
  overlap (50 words) prevents ideas from being split cleanly in half across
  chunk boundaries.
- **Top-4 retrieval** — a starting point; a reasonable middle ground between
  giving the model enough context and keeping the prompt small.

## What's working
- Full pipeline tested end-to-end: upload → chunk → embed → store → retrieve
  → answer.
- Validated specifically against the exact failure case from v1 — the same
  class of large document that broke v1 now works cleanly in v2.
- Tested on both narrative (Project Gutenberg text) and structured academic
  content (arXiv survey paper), with retrieval correctly surfacing different,
  relevant sections for different questions.
- Custom frontend shows chunk count on upload and "chunks used" per answer,
  making retrieval visible and explainable during a demo.

## Known limitations
- **Retrieval quality is approximate** — semantic similarity search doesn't
  guarantee the "correct" chunks are always retrieved, especially for
  questions that need information spread across many non-adjacent parts of
  a document.
- **Fixed top-k (4 chunks)** — not adaptive; a very broad question might
  need more context than 4 chunks provide, while a narrow question might
  only need one.
- **No persistence beyond ChromaDB's local files** — works for a single-
  machine demo; not set up for multi-user or cloud deployment.
- **Chunking is naive** — splits by raw word count, not by sentence or
  paragraph boundaries, so a chunk can still start or end mid-sentence
  (the overlap mitigates but doesn't fully solve this).

## What's next
1. Compare answer quality and behavior side-by-side against v1 on the same
   small PDFs, to document where RAG helps and where it doesn't change much.
2. Experiment with chunk size, overlap, and top-k values to see their effect
   on answer quality.
3. Try sentence/paragraph-aware chunking instead of raw word-count chunking.

## Why this approach
v1 proved the core LLM app mechanics and exposed a real limitation. v2
directly addresses that limitation using the standard technique built for
exactly this problem: retrieval-augmented generation. Building both versions
made the value of RAG concrete rather than theoretical, it wasn't adopted
because it's the "standard" way to do it, but because it visibly solved a
failure this project actually hit.

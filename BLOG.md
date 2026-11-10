# Building Aegis: A More Trustworthy RAG Pipeline with Verifiable Citations

When I started building Aegis, I expected the hardest part to be getting a retrieval-augmented generation (RAG) system to answer questions. The harder problem was making sure it answered the right person, from the right version of a document, with evidence a human could check. That led me to build an enterprise-style assistant around a simple question: what needs to be true before a company can trust an AI-generated answer?

To explore that question, I modeled a company with HR, finance, engineering, and support teams. Each team owns documents that may be public, internal, or restricted to its department. Employees should be able to ask questions in plain language instead of searching a shared drive—but an HR employee should not retrieve engineering's restricted documents, and the demo's guest account should only see public material. In Aegis, the database applies those visibility rules as part of retrieval, before candidate chunks reach the reranker or answer model.

## Why "Tutorial RAG" Breaks in Production

### The Real-World Problem

A typical RAG tutorial ends with a satisfying flow:

`load → chunk → embed → top-k → answer`

That is a useful starting point, but it leaves out problems that show up as soon as the documents and users belong to a real organization:

- **Everyone can see the same results.** Without access rules in retrieval, an engineering employee could receive HR-only material.
- **Old and new policies get mixed together.** An append-only ingestion flow can leave outdated content searchable alongside its replacement. In Aegis, distinct versions must be marked with the right status in their metadata; replacing the same title and version deletes the previous rows.
- **Vector search can miss exact references.** A question about a policy ID or section title needs lexical matching as well as semantic similarity.
- **Citations can look convincing without being checked.** Without verification and an audit record, it is difficult to establish what supported an answer—or why the system refused.

These are not problems a better prompt can solve on its own. The system needs explicit rules for identity, document versions, retrieval, verification, and recording what happened. Aegis is a small project rather than a production-ready security product, but it gives me a place to work through those engineering boundaries and test them.

### How Aegis Engineers the Fix

Aegis uses a bounded pipeline rather than an open-ended agent: identify the user, classify whether the question asks for history, retrieve permitted material, judge whether it is sufficient, correct the query once if needed, generate and verify an answer, and record the outcome. If the sufficiency check still finds too little support after the retry, the pipeline refuses rather than guessing. Identity is demo-only: the API accepts a username from the request, so a caller can claim another seeded username. A real deployment would need to authenticate the caller and derive identity from a trusted session or token.

### The Pipeline Diagram

![Aegis RAG pipeline diagram](Blog_Digrams/rag_pipeline_v1.png)

- The flow is bounded: an insufficient first search can trigger one query rewrite and another attempt, not an unlimited agent loop.
- SQL applies document visibility and history rules before chunks are ranked.
- Retrieval combines PostgreSQL vector search with PostgreSQL full-text search, then reranks the fused candidates.
- The answer includes citations whose quoted text is checked against the retrieved chunks, and the outcome is written to the audit table.

### Walking Through the Diagram and Why It Matters

The first step loads the user's department and employee status from PostgreSQL. A small intent-classification call then decides whether to include historical documents; when history is requested, the query can include both active and superseded documents that are still stored. Ordinary searches exclude documents marked superseded, so older versions need the right status in their uploaded metadata—Aegis does not assign that status automatically. This matters for questions such as “What did the policy say before the update?” without mixing correctly marked old versions into current-policy searches.

Next, Aegis searches only documents the user is allowed to read. It combines semantic search with PostgreSQL full-text search, merges their rankings, and asks a reranker to score the strongest candidates. The keyword leg uses PostgreSQL's `tsvector`/`ts_rank` full-text search—not BM25—alongside pgvector's semantic search. If the retrieved chunks do not appear sufficient, the system rewrites the query and tries once more; it then answers from the available evidence or returns an explicit refusal.

Finally, the answer model supplies citations and quoted sentences, and Python checks whether each accepted quote appears in its cited chunk. For requests that complete the normal answer-or-refusal flow, a live trace shows key decisions and a separate audit row records the user, question, answer status, grounding status, and sources. The quote check establishes that text is present; it does not prove that the quote entails every claim, and the audit row does not persist the full trace. Those limits are part of the project too, and I will return to them in the sections below.

## System Architecture & Strict Data Contracts

## Content-Addressable Ingestion & Two-Level Splitting

## Security Before Retrieval: SQL Access Control & The "Time-Travel" Intent Switch

## Single-Trip Hybrid Search, Reranking & The Corrective Loop

## Citation-Checked Generation & Deterministic Quote Verification

## Radical Auditability: The Live Execution Trace

## What I Learned Building a More Trustworthy RAG Pipeline

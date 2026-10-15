# Aegis

**Secure, grounded answers from your internal documents.**

Access control is enforced before retrieval. Every claim is quoted and verified. Versions are tracked. Every query is audited.

---

Aegis is a production-oriented RAG system built for company policies and internal knowledge. Employees ask questions in plain language. The system returns cited answers — and never shows them documents they are not allowed to see.

Unlike most RAG demos, permissions are applied in SQL *before* any search runs. A restricted document is never a candidate, never reranked, and never seen by the model.

## Why it exists

Shared drives and wikis make it hard to find the current rule. Generic RAG systems make it worse: they ignore access control, mix superseded policies with current ones, and generate ungrounded answers.

Aegis treats those problems as first-class:

- Department-level access (public / internal / restricted)
- Active vs superseded document versions
- Exact-quote grounding checked in code
- Hybrid search (vector + keyword) with reciprocal rank fusion
- Full audit trail of every question

## Quick start

```bash
# 1. Start the database
docker compose up -d

# 2. Configure
cp .env.example .env
# set OPENAI_API_KEY

# 3. Run
uv run uvicorn assistant.api:app --reload
```

Open http://localhost:8000. Upload Markdown policies (with the required header) and ask questions as different users.

Demo users are seeded:

| User  | Department  | Can see                                      |
| ----- | ----------- | -------------------------------------------- |
| alice | engineering | public + internal + restricted engineering   |
| bob   | hr          | public + internal + restricted hr            |
| carol | finance     | public + internal + restricted finance       |
| guest | —           | public only                                  |

## How it works

1. **Intent** — Detects whether the question is about the current rule or historical versions.
2. **Retrieve** — Hybrid search (pgvector HNSW + Postgres full-text) inside the user’s readable set, then LLM reranking with a score cutoff.
3. **Grade / rewrite** — If context is insufficient, rewrite the query once and try again.
4. **Generate** — Answer from the retrieved chunks only. Every claim must include an exact quote.
5. **Verify** — Quotes are checked in Python against the source chunk (no model involved). Failed quotes trigger a retry.
6. **Record** — Write an audit row and return a human-readable trace.

Access control lives in the readable CTE of the hybrid search query. The permission filter cannot be bypassed by a different code path.

## Features

- **Access control before retrieval** — Restricted documents never leave the database for unauthorized users.
- **Hybrid search + RRF** — Semantic and keyword results fused in one SQL statement.
- **Rerank + score gate** — Low-quality chunks are dropped before they reach the answer model.
- **Grounded generation** — Exact quotes verified in code. Ungrounded claims are rejected.
- **Versioning** — Title + version identity. Intent decides whether superseded documents are searchable.
- **Content-hash deduplication** — Re-uploading identical content is free. Edits replace the previous chunks.
- **Audit trail** — Who asked what, which sources were used, whether the answer was grounded.
- **Trace** — Every response includes a step-by-step log of retrieval decisions and searchable chunk counts.
- **Freshness warnings** — Stale documents are flagged automatically.

## Stack

| Piece         | Choice                                              |
| ------------- | --------------------------------------------------- |
| Language      | Python                                              |
| API           | FastAPI + Uvicorn                                   |
| Models        | OpenAI (`gpt-4o-mini`, `text-embedding-3-small`)    |
| Orchestration | LangChain                                           |
| Database      | PostgreSQL 17 + pgvector (Docker)                   |
| Search        | Hybrid (vector + full-text) with RRF                |
| UI            | Single HTML page                                    |

## Document format

Every file must begin with a header:

```markdown
---
title: Leave policy
department: hr
visibility: internal
version: 1
status: active
effective: 2026-06-30
updated: 2026-06-30
---

# Leave policy

## How many leaves
...
```

- `visibility` is `public`, `internal`, or `restricted`.
- `status` is `active` or `superseded`.
- Identity is `(title, version)`.

## Project structure

```text
.
├── docker-compose.yml
├── schema.sql
├── assistant/
│   ├── config.py          # All tunable numbers
│   ├── models.py
│   ├── ingestion.py       # Parse, hash, split, embed
│   ├── repository.py      # All SQL
│   ├── retrieval.py       # Hybrid search + rerank
│   ├── generation.py      # Answer + quote verification
│   ├── pipeline.py        # End-to-end flow
│   └── api.py
├── prompts/               # answer, grade, intent, rerank, rewrite
└── web/index.html
```

## Configuration

All important knobs live in one file (`assistant/config.py`):

- Chunk size and overlap
- Candidate count and final top-k
- Minimum rerank score and high-confidence shortcut
- Maximum retrieval attempts
- Stale document threshold

Prompts live as plain text files so they can be edited without touching code.

## Security model

| Visibility | Who can read it                         |
| ---------- | --------------------------------------- |
| public     | Anyone (including guests)               |
| internal   | Any employee                            |
| restricted | Only the owning department              |

The filter runs inside the search query. Retrieved means exposed — so unauthorized text is never retrieved.

## API

| Method | Path          | Description                      |
| ------ | ------------- | -------------------------------- |
| GET    | `/`           | Web UI                           |
| GET    | `/health`     | Database status                  |
| GET    | `/documents`  | List indexed documents           |
| POST   | `/documents`  | Upload and index a file          |
| POST   | `/ask`        | Ask a question as a given user   |

In a real deployment the username comes from the authenticated session. The rest of the system already expects a `User` loaded from the database.

## Production notes

The layering follows the same discipline as a typical backend service: the repository owns SQL, services own behavior, the API owns HTTP.

What remains for a production deployment:

- Authentication (JWT / OIDC) so the caller identity is not taken from the request body
- Rate limiting and request size limits
- Structured logging and metrics
- Backup strategy for the Postgres volume

The current design makes those additions local.

## License

MIT

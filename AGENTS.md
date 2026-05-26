# AGENTS.md — Funes

This repo hosts LLM-managed **knowledge bases**, one per top-level folder. The
pattern (adapted from [Karpathy's "LLM Knowledge Bases"](https://x.com/karpathy/status/2039805659525644595)):
raw sources are compiled by an LLM ("the Librarian") into an interlinked markdown
wiki, then queried and incrementally improved — all plain markdown in git.

## Folders

- **[`starter-library/`](./starter-library/)** — a ready-to-use, empty
  Librarian-managed knowledge base; the reference implementation of the pattern.
  Copy or rename it per topic, or use it as-is. Add more top-level folders to run
  several separate libraries in one repo.

## Working inside a library

Each library is governed by its own `AGENTS.md`. **Read that file before acting**
within the folder. Managed libraries share one operating manual: the
**[Librarian Protocol](./protocol.md)** — the full ingest → compile → Q&A →
health-check workflow, conventions, and templates.

## Creating a new library

See **[`library.md`](./library.md)** for the full setup recipe — the conventions
to confirm, the standard structure, and what a library's `AGENTS.md` must cover.

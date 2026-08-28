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

## Shared tools

Use [`tools/check_links.py`](./tools/check_links.py) and
[`tools/compile_lint.py`](./tools/compile_lint.py) for the mechanical parts of a
health check. Use [`tools/pdf_text.py`](./tools/pdf_text.py) to create
provenance-marked searchable sidecars for PDFs, with OCR only where native text
is missing or sparse. For targeted inspection of a known public YouTube source,
[`tools/youtube_transcript.py`](./tools/youtube_transcript.py) can retrieve
available captions after its optional dependency is installed. See
[`tools/README.md`](./tools/README.md) for commands, limits, and research
standards.

# Starter Library

A self-improving, LLM-maintained knowledge base. You feed in raw sources and ask
questions; an LLM **Librarian** does the writing, organizing, linking, and
upkeep. The wiki is plain markdown, viewable on GitHub or in any editor.

This library ships **empty** — it's your starting point. Rename the folder to
suit your topic if you like, and update the **Scope** line in
[`AGENTS.md`](./AGENTS.md).

Inspired by [Andrej Karpathy's "LLM Knowledge Bases" workflow](https://x.com/karpathy/status/2039805659525644595),
adapted to live inside a git repo instead of Obsidian.

## Layout

```
starter-library/
├── AGENTS.md        ← the Librarian's operating manual (start here)
├── README.md        ← this file — human-facing overview + how to use
├── raw/             ← verbatim source documents (immutable)
│   └── INDEX.md     ← registry of all sources
├── wiki/            ← the compiled, interlinked knowledge base
│   ├── INDEX.md     ← master navigation
│   ├── sources/     ← one summary note per raw source
│   ├── concepts/    ← atomic articles (one idea each)
│   └── topics/      ← maps of related concepts
├── outputs/         ← generated reports / analyses (filed back when durable)
└── meta/            ← changelog and health-check reports
```

## Adding material

- **In chat:** paste text, drop a link, or describe a source → "ingest this." Best
  for quick captures (if a URL can't be fetched, paste the text).
- **Via `raw/`:** commit files into `raw/`, then "ingest the new sources in `raw/`."
  Best for PDFs, images, web clips, or batches — no need to name files or edit the
  index; the Librarian does that.

Files/PDFs/images/batches → `raw/`; quick text/links → chat. Material persists only
once committed.

## Using it

Ask questions (answered with citations; substantial outputs go to `outputs/`), or
ask for a "health check" to audit links, duplicates, gaps, and new-article
candidates. You rarely edit the wiki by hand — that's the Librarian's job. See
[`AGENTS.md`](./AGENTS.md) and the shared [protocol](../protocol.md).

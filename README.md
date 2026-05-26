# Funes

Funes is a Git-based framework for LLM-managed knowledge work.

An AI “Librarian” ingests raw sources, preserves them as an immutable record, compiles them into an interlinked Markdown wiki, and uses that wiki to produce cited reports, analyses, routines, and answers. You provide the sources and questions; the Librarian handles the writing, linking, indexing, health checks, and upkeep.

Everything lives in plain Markdown inside a Git repo, so your knowledge base is versioned, diffable, portable, searchable, and usable from GitHub or any editor.

The workflow is inspired by
[Andrej Karpathy's "LLM Knowledge Bases"](https://x.com/karpathy/status/2039805659525644595) idea,
adapted for Git instead of Obsidian.

## Origin of the name

"[Funes the Memorious](https://en.wikipedia.org/wiki/Funes_the_Memorious)" — This tool is Funes with the ability to abstract.

## How it works

```
raw source ─ingest→ raw/             (verbatim, immutable)
           ─compile→ wiki/sources/   (one summary note per source)
                   → wiki/concepts/  (atomic articles, one idea each)
                   → wiki/topics/    (maps of content grouping concepts)
question   ─answer→ read wiki, cite articles
           ─output→ outputs/  →(if durable)→ filed back into wiki
```

You rarely edit the wiki by hand — that's the Librarian's job. You supply
sources and ask questions; the agent maintains the structure, links, and indexes.

## Quick start

1. **Use this repository as a template** (GitHub's "Use this template" button) or
   clone it.
2. **Open it with an agentic coding tool** (e.g. Claude Code, or any LLM agent
   that can read files and run a repo). The agent reads [`AGENTS.md`](./AGENTS.md)
   to learn how to behave as the Librarian.
3. **Add sources.** Drop PDFs, web clips, or notes into
   [`starter-library/raw/`](./starter-library/raw/) and say *"ingest the new
   sources in `raw/`,"* or just paste text / a link in chat and say *"ingest
   this."*
4. **Ask questions.** The Librarian answers with citations into the wiki, writes
   substantial outputs to `outputs/`, and offers to file durable findings back in.
5. **Keep it healthy.** Periodically ask for a *"health check"* to audit broken
   links, duplicate concepts, stale indexes, and gaps.

Rename or copy [`starter-library/`](./starter-library/) to suit your topic (e.g.
`physics/`), or just use it as-is. To run several separate knowledge bases in one
repo, add more top-level library folders — see [`library.md`](./library.md).

## What's in here

- **[`starter-library/`](./starter-library/)** — a ready-to-use, **empty**
  knowledge base: the standard `raw / wiki / outputs / meta` scaffold with seed
  index files. This is your starting point; it ships empty so your KB begins
  clean.
- **[`AGENTS.md`](./AGENTS.md)** — entry point for agents: what each folder is and
  how to work in the repo.
- **[`protocol.md`](./protocol.md)** — the shared **Librarian Protocol**: the full
  ingest → compile → Q&A → health-check workflow, conventions, and article
  templates.
- **[`library.md`](./library.md)** — recipe for spinning up additional libraries
  in the same repo.

## Example — what the Librarian produces

You never write these by hand; this is just to show the shape of the output. The
full templates live in [`protocol.md`](./protocol.md).

A **source note** (`wiki/sources/attention-is-all-you-need.md`) summarizing a raw
source and linking to the concepts it feeds:

```markdown
---
title: Attention Is All You Need
type: source
tags: [transformers, attention]
created: 2026-01-10
updated: 2026-01-10
---
# Attention Is All You Need
- **Raw file:** [2026-01-10-attention-is-all-you-need.pdf](../../raw/2026-01-10-attention-is-all-you-need.pdf)
- **Original:** https://arxiv.org/abs/1706.03762

## Summary
Introduces the Transformer, a sequence model based entirely on attention,
dropping recurrence and convolution.

## Key takeaways
- Self-attention relates all positions in a sequence in O(1) sequential steps.
- Multi-head attention lets the model attend to different subspaces at once.

## Concepts extracted
- [Self-attention](../concepts/self-attention.md)
- [Multi-head attention](../concepts/multi-head-attention.md)
```

An **atomic concept** (`wiki/concepts/self-attention.md`), densely backlinked:

```markdown
---
title: Self-attention
type: concept
tags: [transformers]
created: 2026-01-10
updated: 2026-01-10
---
# Self-attention
A mechanism that computes a representation of a sequence by relating each
position to every other position, weighting them by learned compatibility.

## Related
- [Multi-head attention](./multi-head-attention.md)
## Sources
- [Attention Is All You Need](../sources/attention-is-all-you-need.md)
## Topics
- [Transformer architecture](../topics/transformer-architecture.md)
```

## Credits

Pattern adapted from
[Andrej Karpathy's "LLM Knowledge Bases"](https://x.com/karpathy/status/2039805659525644595).

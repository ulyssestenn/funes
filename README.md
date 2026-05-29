# Funes

Funes turns folders of raw sources into a durable, cited Markdown knowledge base maintained by an AI Librarian.

Drop in PDFs, transcripts, web clips, screenshots, notes, articles, or pasted text. The Librarian preserves the raw record, compiles it into an interlinked wiki, and uses that wiki to produce cited answers, reports, reading plans, comparisons, routines, syntheses, and other reusable outputs. Built for researchers, students, and hobbyists.

Everything lives in plain Markdown inside a Git repo, so your knowledge base is versioned, diffable, portable, searchable, and usable from GitHub or any editor.

Funes is not a chatbot over files. It creates a maintained knowledge library.

## See it in action

Here is an [example library](https://github.com/ulyssestenn/funes-example-ai) you can browse to see the type of output you can expect from Funes.

## Origin of the name

Funes is named after Borges's “[Funes the Memorious](https://en.wikipedia.org/wiki/Funes_the_Memorious),” a character who remembers everything but cannot abstract.

This project preserves the raw record, then abstracts it into concepts, topics, and usable outputs.

## How it works

```text
raw source ─ingest→ raw/             (verbatim, immutable)
           ─compile→ wiki/sources/   (one summary note per source)
                   → wiki/concepts/  (atomic articles, one idea each)
                   → wiki/topics/    (maps of related concepts)

question   ─answer→ read wiki, cite articles
           ─output→ outputs/         (reports, analyses, routines, answers)
                   → wiki/           (durable findings filed back in)
```

The wiki is not the end product. It is the working memory the Librarian uses to answer questions, generate reports, produce routines, notice gaps, and keep the knowledge base coherent over time.

You rarely edit the wiki by hand. You supply sources and questions; the Librarian maintains the structure, links, indexes, and outputs.

## Design
 
- **Plain Git, not Obsidian or a cloud app** — your knowledge base is versioned, diffable, browsable on GitHub, and readable by any agent.
- **Many libraries, one repo** — each top-level folder is an independent knowledge base sharing a single Librarian protocol.
- **A three-tier wiki** — `sources/` (one summary per document), `concepts/` (one idea each), and `topics/` (maps across concepts), linked bidirectionally.
- **An immutable raw layer** — originals are preserved verbatim and never edited; all abstraction happens in the wiki tier above.
- **Self-maintenance built in** — an append-only changelog, dated health reports, and audits for contradictions, gaps, duplicate concepts, and stale links.

## Quick start

1. **Use this repository as a template** with GitHub's “Use this template” button, or clone it.

2. **Point your agentic coding tool of choice at your repo.** Use Claude Code, Codex, or any LLM agent that can read and edit files in a repo. The agent reads [`AGENTS.md`](./AGENTS.md) to learn how to behave as the Librarian.

3. **Add sources.** Drop PDFs, web clips, notes, or other materials into [`starter-library/raw/`](./starter-library/raw/) and say:

   > ingest the new sources in `raw/`

   Or paste text or a link directly in chat and say:

   > ingest this

4. **Ask questions.** The Librarian answers with citations into the wiki, writes substantial outputs to `outputs/`, and offers to file durable findings back into the knowledge base.

5. **Keep it healthy.** Periodically ask for a “health check” to audit broken links, duplicate concepts, stale indexes, contradictions, gaps, and possible new articles.

Rename or copy [`starter-library/`](./starter-library/) to suit your topic, such as `physics/`, `history/`, `research/`, or `personal-kb/`. To run several separate knowledge bases in one repo, add more top-level library folders. See [`library.md`](./library.md).

## What's in here

- **[`starter-library/`](./starter-library/)** — a ready-to-use empty knowledge base with the standard `raw / wiki / outputs / meta` scaffold and seed index files.
- **[`AGENTS.md`](./AGENTS.md)** — the entry point for agents: what each folder is and how to work in the repo.
- **[`protocol.md`](./protocol.md)** — the shared Librarian Protocol: the full ingest → compile → Q&A → output → health-check workflow, plus conventions and article templates.
- **[`library.md`](./library.md)** — the recipe for creating additional libraries in the same repo.

## Example — what the Librarian produces

You do not write these by hand. They show the shape of the compiled wiki. The full templates live in [`protocol.md`](./protocol.md).

A **source note** summarizes a raw source and links to the concepts it feeds:

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

Introduces the Transformer, a sequence model based entirely on attention, dropping recurrence and convolution.

## Key takeaways

- Self-attention relates all positions in a sequence in O(1) sequential steps.
- Multi-head attention lets the model attend to different subspaces at once.

## Concepts extracted

- [Self-attention](../concepts/self-attention.md)
- [Multi-head attention](../concepts/multi-head-attention.md)
```

An **atomic concept** explains one idea and links it back to sources, related concepts, and topic maps:

```markdown
---
title: Self-attention
type: concept
tags: [transformers]
created: 2026-01-10
updated: 2026-01-10
---

# Self-attention

A mechanism that computes a representation of a sequence by relating each position to every other position, weighting them by learned compatibility.

## Related

- [Multi-head attention](./multi-head-attention.md)

## Sources

- [Attention Is All You Need](../sources/attention-is-all-you-need.md)

## Topics

- [Transformer architecture](../topics/transformer-architecture.md)
```

An **output** is a substantial answer, report, routine, or analysis generated from the wiki:

```markdown
# Reading plan for understanding Transformers

This plan draws on the compiled notes for [Attention Is All You Need](../wiki/sources/attention-is-all-you-need.md), [Self-attention](../wiki/concepts/self-attention.md), and [Multi-head attention](../wiki/concepts/multi-head-attention.md).

## Goal

Understand why the Transformer replaced recurrence for many sequence-modeling tasks.

## Sequence

1. Read the source note for *Attention Is All You Need*.
2. Review the concept article on self-attention.
3. Review multi-head attention.
4. Compare the topic map on Transformer architecture against the original paper.

## Durable findings to file back

- Add a concept article on positional encoding.
- Add a topic map for sequence modeling.
```

## License

Funes is © 2026 Bethany Hunt, licensed under the GNU Affero General Public License v3.0. You're free to use, modify, and share it; if you run it or a derivative as a network service, you must make your source available to that service's users. Commercial licensing, to use Funes inside a closed product, is available on request: bhuntdev+funes@gmail.com.


## Acknowledgments

Funes is inspired by [Andrej Karpathy's "LLM Knowledge Bases"](https://x.com/karpathy/status/2039805659525644595) and by the Librarian framing of Systems Made Better's [*Build a Claude Knowledge Base That Self-Improves*](https://www.youtube.com/watch?v=ib74sLgjIBM).



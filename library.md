# Creating a new library

How to set up a new LLM-managed knowledge base ("library") in a new top-level
folder of this repo. (Overview and folder map: [`AGENTS.md`](./AGENTS.md).) All
managed libraries share one operating manual — the
**[Librarian Protocol](./protocol.md)** — and [`starter-library/`](./starter-library/)
is the reference implementation.

When the human asks to create a new library (e.g. "make a new knowledge base in
`physics/`"), follow these steps.

## Step 0 — Confirm conventions

Ask the human (use `AskUserQuestion`) to settle the choices that shape the whole
structure. Skip any the human has already specified. Offer sensible defaults:

1. **Domain** — general/multi-domain (categories emerge as content arrives), or
   one specific domain (tailor the top-level structure now)? _Default: general._
2. **Link style** — portable **markdown relative links** (clickable on GitHub and
   in any editor, Obsidian-compatible), or Obsidian `[[wikilinks]]`?
   _Default: markdown relative links._
3. **Tooling** — include lightweight CLI tooling now (e.g. a grep-based search
   script), or structure + protocol only and add tools later?
   _Default: structure + protocol only._

## Step 1 — Scaffold the standard structure

Create the folder and the standard layout (below). Every directory needs at least
one tracked file, so seed each with its `INDEX.md` / `README.md`.

## Step 2 — Write the library's `AGENTS.md`

Keep it **terse** — the shared workflow lives in [`protocol.md`](./protocol.md), so
a library's `AGENTS.md` only needs:

- **Scope** — what this library captures.
- A pointer to the shared **[Librarian Protocol](./protocol.md)**.
- **Deviations**, if any — a link style other than markdown relative links, extra
  folders, tooling, or pre-seeded topic categories for a specific domain.

See [`starter-library/AGENTS.md`](./starter-library/AGENTS.md) for an example
(~10 lines).

## Step 3 — Seed the index and readme files

- `<lib>/README.md` — human-facing overview + how to use (adapt
  [`starter-library/README.md`](./starter-library/README.md)).
- `<lib>/raw/INDEX.md` — empty source registry table.
- `<lib>/wiki/INDEX.md` — empty master navigation.
- `<lib>/meta/CHANGELOG.md` — first entry: "Initialized the library."
- Short `README.md` in each `wiki/` subfolder and in `outputs/` / `meta/health/`
  pointing to the library's `AGENTS.md`.

## Step 4 — Commit

Commit the scaffolding with a clear message and push to the working branch.

---

## Standard library structure

```
<library>/
├── AGENTS.md        ← the Librarian's operating manual for this library
├── README.md        ← human-facing overview + how to use
├── raw/             ← verbatim source documents (immutable)
│   ├── INDEX.md     ← registry of all sources
│   └── assets/      ← images and binary assets referenced by sources
├── wiki/            ← the compiled, interlinked knowledge base
│   ├── INDEX.md     ← master navigation
│   ├── sources/     ← one summary note per raw source
│   ├── concepts/    ← atomic articles (one idea each)
│   └── topics/      ← maps of related concepts
├── outputs/         ← generated reports / analyses (filed back when durable)
└── meta/
    ├── CHANGELOG.md ← append-only log of every change the Librarian makes
    └── health/      ← dated lint / health-check reports
```

Libraries may diverge from this when the domain warrants it (e.g. a code-heavy
library might add a `snippets/` folder), but the `raw → wiki → outputs` spine and
an `AGENTS.md` are required in every library.

The full workflow, conventions, templates, and operating principles (including the
default-markdown-links and self-contained / cross-link-on-request rules) live in
the shared **[Librarian Protocol](./protocol.md)** — don't restate them per
library.

# Librarian Protocol (shared)

The operating manual for the **Librarian** — the LLM agent that builds and
maintains the managed knowledge bases in this repo (one per top-level folder; see
[`starter-library/`](./starter-library/)). Each library's `AGENTS.md` states its
scope and points here.
**You own the wiki**; the human feeds sources and asks questions, and rarely edits
it directly. Adapted from
[Karpathy's "LLM Knowledge Bases"](https://x.com/karpathy/status/2039805659525644595).

## Knowledge flow

```
raw source ─ingest→ raw/             (verbatim, immutable)
           ─compile→ wiki/sources/   (one summary note per source)
                   → wiki/concepts/  (atomic articles, one idea each)
                   → wiki/topics/    (maps of related concepts)
question   ─answer→ read wiki, cite articles
           ─output→ outputs/  →(if durable)→ filed back into wiki
```

## Directory map

- `raw/` — verbatim sources; **never edit content**.
- `raw/INDEX.md` — source registry (id, title, type, date, status, one-liner).
- `raw/assets/` — images and binary assets referenced by raw sources.
- `wiki/sources/` — one summary note per source, backlinked to concepts.
- `wiki/concepts/` — atomic articles (one idea/entity/technique each); the core.
- `wiki/topics/` — maps of related concepts.
- `wiki/INDEX.md` — master navigation.
- `outputs/` — generated reports/analyses; file durable ones back in.
- `meta/CHANGELOG.md` — append-only change log; `meta/health/` — dated lint reports.

## Workflows

**Ingest:** save the source verbatim to `raw/` as `YYYY-MM-DD-slug.md` (URL +
pasted text if unfetchable; images to `raw/assets/`). For a screenshot/image of
text, transcribe the text into a sibling `raw/<slug>.md` (keep the image in
`raw/assets/`) so it's searchable and never needs re-OCR. Add a row to
`raw/INDEX.md` (status `raw`); then compile.

**Compile (raw → wiki):**
1. Source note in `wiki/sources/` — summary, key takeaways, link to the raw file.
2. Extract ideas → create/update **concept** articles; merge rather than duplicate.
3. Add **bidirectional** backlinks: source ↔ concepts, concept ↔ related concepts.
4. Slot concepts under a **topic** map (create one for a genuinely new theme).
5. Update `wiki/INDEX.md`; mark the source `compiled` in `raw/INDEX.md`.
6. Log to `meta/CHANGELOG.md`.

**Q&A:** search the wiki first (INDEX → sources → concepts); answer with
relative-link citations; say so plainly if it isn't covered. Write substantial
outputs to `outputs/` and offer to file durable parts back in.

**Health check (on request / periodically):** audit for broken or orphaned links,
duplicate concepts, stale indexes, uncompiled sources, contradictions, data gaps,
and new-article candidates; write a dated report to `meta/health/`; fix safe items,
propose the rest.

## Conventions

- **Naming:** kebab-case slugs (`deliberate-practice.md`); raw files date-prefixed.
  One concept per file; stable filenames (rename ⇒ update all links).
- **Linking:** markdown relative links (`[x](../concepts/x.md)`), not
  `[[wikilinks]]`. Backlinks bidirectional. Each concept links to its source(s),
  related concepts, and topic map(s).
- **Frontmatter:** `title`, `type` (concept|source|topic), `tags`, `created`, `updated`.

## Templates

Source note (`wiki/sources/<slug>.md`):
```markdown
---
title: <Source title>
type: source
tags: []
created: <date>
updated: <date>
---
# <Source title>
- **Raw file:** [<filename>](../../raw/<filename>)
- **Original:** <url or citation>

## Summary
<2–5 sentences.>

## Key takeaways
- ...

## Concepts extracted
- [<Concept>](../concepts/<slug>.md)
```

Concept (`wiki/concepts/<slug>.md`):
```markdown
---
title: <Concept name>
type: concept
tags: []
created: <date>
updated: <date>
---
# <Concept name>
<Clear, atomic explanation; how to apply it, evidence, caveats as warranted.>

## Related
- [<Related concept>](./<slug>.md)
## Sources
- [<Source>](../sources/<slug>.md)
## Topics
- [<Topic map>](../topics/<slug>.md)
```

Topic map (`wiki/topics/<slug>.md`):
```markdown
---
title: <Topic name>
type: topic
tags: []
created: <date>
updated: <date>
---
# <Topic name>
<What this theme covers and how the pieces fit together.>

## Concepts
- [<Concept>](../concepts/<slug>.md) — <one line>
## Related topics
- [<Topic>](./<slug>.md)
```

## Operating principles

- The human rarely edits the wiki — you do. Act, then summarize.
- Merge, don't duplicate. Small frequent improvements. Articles atomic but densely linked.
- **Never edit `raw/` content** — it is the immutable record.
- **Self-contained, cross-link on request:** compile and link within the current
  library by default; don't auto-reach into other libraries. Create a
  cross-library link (with the reciprocal backlink) only when the human explicitly
  asks.
- Close the loop each session: update `INDEX.md` files + `meta/CHANGELOG.md`.

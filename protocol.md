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
`raw/assets/`) so it's searchable and never needs re-OCR. For a PDF or other
binary document whose text you extract, save the extracted text as a sibling
`raw/<slug>.txt` or `raw/<slug>.htm`; if extraction is partial, note the pages it
covers. Keep the binary as the verbatim original so it never needs re-extraction.
Add a row to `raw/INDEX.md` (status `raw`); then compile.

**Compile (raw → wiki):**
1. Source note in `wiki/sources/` — summary, key takeaways, link to the raw file.
2. Extract ideas → create/update **concept** articles; merge rather than duplicate.
3. Add **bidirectional** backlinks: source ↔ concepts, concept ↔ related concepts.
4. Slot concepts under a **topic** map (create one for a genuinely new theme).
5. Update `wiki/INDEX.md`; mark the source `compiled` in `raw/INDEX.md`.
6. Log to `meta/CHANGELOG.md`.

*Depth is the point of compiling.* A source note's summary and takeaways must be
specific to that source, and a concept article must carry the actual substance:
named frameworks, numbered schemes, key terms, telling examples, and material
caveats. Templated summaries, takeaways that only restate a concept's one-line
lead, and stub articles that discard most of a source mean extraction did not
happen. Redo the compile rather than padding it. The depth gates in
[`tools/compile_lint.py`](./tools/compile_lint.py) catch common mechanical forms
of these failures.

**Q&A:** search the wiki first (INDEX → sources → concepts); answer with
relative-link citations; say so plainly if it isn't covered. Write substantial
outputs to `outputs/` and offer to file durable parts back in.

**Health check (on request / periodically):** audit for broken or orphaned links,
duplicate concepts, stale indexes, uncompiled sources, contradictions, data gaps,
and new-article candidates; write a dated report to `meta/health/`; fix safe items,
propose the rest. Run the mechanical link, orphan, and frontmatter checks with
[`tools/check_links.py`](./tools/check_links.py), for example `python3
tools/check_links.py <library> --orphans --front`. Run the compile-depth checks
with [`tools/compile_lint.py`](./tools/compile_lint.py), for example `python3
tools/compile_lint.py <library>`. The latter gates templated or duplicated prose
and echo takeaways while treating short notes and high compression as advisories
to investigate, not targets to pad. Both linters run in CI; duplicate,
contradiction, grounding, and gap review beyond them remains editorial.

## Conventions

- **Naming:** kebab-case slugs (`deliberate-practice.md`); raw files date-prefixed.
  One concept per file; stable filenames. A rename means updating every link,
  including historical entries in `meta/CHANGELOG.md`, and logging the sweep.
- **Linking:** markdown relative links (`[x](../concepts/x.md)`), not
  `[[wikilinks]]`. Backlinks bidirectional. Each concept links to its source(s),
  related concepts, and topic map(s).
- **Frontmatter:** `title`, `type` (concept|source|topic), `tags`, `created`, `updated`.

## Cross-library links

Libraries are self-contained by default, but the repository is one tree. A link
to another library is an ordinary relative Markdown path, for example
`[Concept](../../../other-library/wiki/concepts/concept.md)` from a file under
`wiki/concepts/`, `wiki/sources/`, or `wiki/topics/` (use two `../` segments
from `wiki/INDEX.md`). These links stay clickable in GitHub and editors.

- **Propose, then write.** When compiling reveals a strong, substantive tie to
  another library, propose it to the human and add it after approval. Do not
  silently add loose "see also" associations.
- **Label and isolate.** Put cross-library links under `## Related (other
  libraries)`, separate from in-library links, and label the target library and
  the reason for the connection.
- **Make links reciprocal.** Add a backlink in the target file. Renaming or
  moving either file means repairing its partner link too.
- **Give shared concepts one home.** Store a concept in its most fundamental
  library and link to it elsewhere instead of duplicating it.
- **Advertise useful connections.** When a library has cross-links, add a short
  `Connected libraries` note near the top of its `wiki/INDEX.md` so the
  Librarian can decide whether to follow them.

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
- **Self-contained, cross-link deliberately:** compile and link within the
  current library by default. For a genuine connection, follow
  [Cross-library links](#cross-library-links): propose it, get approval, then add
  the link and reciprocal backlink.
- Close the loop each session: update `INDEX.md` files + `meta/CHANGELOG.md`.

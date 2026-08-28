#!/usr/bin/env python3
"""Lint compiled wiki notes for shallow-compile failure modes.

Companion to ``check_links.py``. Where that script checks the link *graph*, this
one checks whether a compile actually did the *extraction* work — catching the
failure mode where every file exists and every link resolves, but the prose is
templated boilerplate or 2-sentence stubs that threw away the source material.

The bug this exists to prevent (buddhism, 2026-05-30 "depth re-compile"): an
ingest produced 73 identical templated source-note summaries ("This transcript
discusses <TITLE>. It has been compiled as a source for the … knowledge base
…") and ~40-word concept stubs that echoed each concept's one-liner — and the
whole thing passed the link/orphan/frontmatter audit cleanly, because nothing
checked for *depth*.

Two tiers, by design
--------------------
GATING (non-zero exit) — checks whose *cheapest way to pass is the behaviour we
want*, so they are safe to enforce:

- **dup**   templated/near-duplicate ``## Summary`` blocks or concept leads. Two
            detectors: (a) a *template* phrase (k-gram) reused across a large
            fraction of notes — what catches the boilerplate-with-variable-slot
            case above; (b) a near-duplicate *pair* (overlap coefficient) — what
            catches a handful of copy-pasted notes. The only way to clear (a) is
            to write genuinely distinct summaries, i.e. to read the sources.
- **echo**  source-note takeaways that merely restate the lead of a concept they
            link — takeaways that teach nothing the concept didn't already say.

ADVISORY (printed; affects exit only under ``--strict``) — proxies that would
*invite gaming* if made targets (a word-count target trains padding), so they
are surfaced for a *reviewer*, never enforced against the writer:

- **depth**  concept bodies under a word floor (review — do not pad), and the
             per-library raw->wiki word ratio (logged for trend; flagged only if
             extreme, e.g. a thin compile leaves a very high ratio).

Deliberately NOT here: an automated *grounding / fidelity* check (does every
proper noun / date in an article appear in its cited source?). It was prototyped
and removed: the raw sources are ASR auto-captions, so correct enrichments fail
a string match ("Blavatsky" appears in the caption only as a garbled
"Theosoph…", years are spoken as words) — it fired on 100% of articles, pure
noise. Worse, a grounding *gate* would train hedging or deletion of true detail.
Fidelity is the job of an adversarial LLM review that actually reads source and
article together — a *process* step, not a regex. See tools/README.md.

Usage
-----
    python3 tools/compile_lint.py                 # whole repo: gates + advisories
    python3 tools/compile_lint.py buddhism        # one library
    python3 tools/compile_lint.py --strict        # advisories also gate

Exit code is non-zero if a *gating* check finds problems (or any check, under
--strict), so it can gate CI alongside check_links.py.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata

CONCEPT_LINK_RE = re.compile(r"\.\./concepts/([a-z0-9-]+)\.md")


def read(path: str) -> str:
    return open(path, encoding="utf-8").read()


def fold(s: str) -> str:
    """Lowercase and strip diacritics so 'Nāgārjuna' folds to 'nagarjuna'."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def libraries(root: str) -> list[str]:
    """Managed-library dirs (those with a wiki/). Accepts repo root or one lib."""
    if os.path.isdir(os.path.join(root, "wiki")):
        return [root]
    out = []
    for n in sorted(os.listdir(root)):
        p = os.path.join(root, n)
        if os.path.isdir(p) and os.path.isdir(os.path.join(p, "wiki")):
            out.append(p)
    return out


def notes_in(lib: str, sub: str) -> list[str]:
    d = os.path.join(lib, "wiki", sub)
    if not os.path.isdir(d):
        return []
    return sorted(
        os.path.join(d, n)
        for n in os.listdir(d)
        if n.endswith(".md") and n not in ("README.md", "INDEX.md")
    )


def section(text: str, heading: str) -> str:
    """Body of the named '## heading' section, up to the next '#'/'##' or EOF."""
    out, capturing = [], False
    for line in text.splitlines():
        if line.strip().lower() == f"## {heading}".lower():
            capturing = True
            continue
        if capturing and re.match(r"^#{1,3}\s", line):
            break
        if capturing:
            out.append(line)
    return "\n".join(out).strip()


def lead_and_body(text: str) -> str:
    """A concept's prose: after the '# Title' line, before the first '## '."""
    out, started = [], False
    for line in text.splitlines():
        if not started:
            if line.startswith("# "):
                started = True
            continue
        if re.match(r"^##\s", line):
            break
        out.append(line)
    return "\n".join(out).strip()


def words(s: str) -> int:
    return len(s.split())


def ngrams(s: str, k: int) -> set:
    toks = re.findall(r"\w+", fold(s))
    if len(toks) < k:
        return {" ".join(toks)} if toks else set()
    return {" ".join(toks[i : i + k]) for i in range(len(toks) - k + 1)}


def overlap(a: set, b: set) -> float:
    """Overlap coefficient |A∩B| / min(|A|,|B|) — robust to length gaps."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


# --------------------------------------------------------------------------- #
# GATING checks
# --------------------------------------------------------------------------- #
def check_duplicates(lib, pair_threshold, template_frac, k=8):
    """Return (template_findings, pair_findings).

    template_findings: list of (phrase, [labels]) — one k-gram reused across
        >= template_frac of notes (the boilerplate-with-variable-slot case).
    pair_findings: list of [labelA, labelB] — a near-duplicate pair by overlap.
    """
    items = []  # (label, k-gram set)
    for n in notes_in(lib, "sources"):
        summ = section(read(n), "Summary")
        if summ:
            items.append((f"{n} (Summary)", ngrams(summ, k)))
    for n in notes_in(lib, "concepts"):
        body = lead_and_body(read(n))
        if body:
            items.append((f"{n} (lead)", ngrams(body, k)))

    # (a) template detection: a k-gram shared by many notes.
    template_findings = []
    if len(items) >= 5:
        gram_owners: dict[str, list[int]] = {}
        for idx, (_, grams) in enumerate(items):
            for g in grams:
                gram_owners.setdefault(g, []).append(idx)
        phrase, owners = max(gram_owners.items(), key=lambda kv: len(kv[1]), default=("", []))
        if owners and len(owners) >= max(5, template_frac * len(items)):
            labels = [items[i][0] for i in owners]
            template_findings.append((phrase, sorted(labels)))

    # (b) near-duplicate pairs by overlap coefficient.
    pair_findings = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if overlap(items[i][1], items[j][1]) >= pair_threshold:
                pair_findings.append(sorted([items[i][0], items[j][0]]))
    return template_findings, pair_findings


def check_echo(lib, threshold):
    """Source-note takeaways/summary lines that just restate a linked concept."""
    leads = {}
    for n in notes_in(lib, "concepts"):
        slug = os.path.basename(n)[:-3]
        first = re.split(r"(?<=[.!?])\s", lead_and_body(read(n)).strip())
        leads[slug] = first[0] if first else ""

    hits = []
    for n in notes_in(lib, "sources"):
        text = read(n)
        scan = section(text, "Key takeaways") + "\n" + section(text, "Summary")
        for line in scan.splitlines():
            for slug in CONCEPT_LINK_RE.findall(line):
                lead = leads.get(slug, "")
                if not lead:
                    continue
                prose = _takeaway_prose(line)
                # A bare label / link with no real prose of its own can't echo —
                # well-formed notes lead a takeaway with "**[Concept](link)**" then
                # explain in their *own* words. Only compare substantive prose.
                if words(prose) < 6:
                    continue
                ls, ps = fold(lead), fold(prose)
                if (ls and ls in ps) or overlap(ngrams(lead, 4), ngrams(prose, 4)) >= threshold:
                    hits.append((n, slug))
    return sorted(set(hits))


def _takeaway_prose(line: str) -> str:
    """The takeaway's own words: strip the leading label and link syntax.

    Handles both the boilerplate shape ("Connects the transcript to [X]: <prose>")
    and the well-formed shape ("**[X](link)** — <prose>"), so we compare a
    takeaway's actual explanation against the concept lead, not its title.
    """
    s = re.sub(r"^[\s\-*]*", "", line)
    s = re.sub(r"^connects the transcript to\s*", "", s, flags=re.I)
    # drop a leading bracketed link or bolded link label, plus any ":" / "—" / "-"
    s = re.sub(r"^\**\[[^\]]*\]\([^)]*\)\**\s*[:—-]*\s*", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # remaining inline links -> text
    return s.strip()


# --------------------------------------------------------------------------- #
# ADVISORY checks
# --------------------------------------------------------------------------- #
def check_depth(lib, floor):
    """Stub concept bodies (< floor words) and the raw->wiki word ratio."""
    stubs, wiki_words = [], 0
    for n in notes_in(lib, "concepts"):
        w = words(lead_and_body(read(n)))
        wiki_words += w
        if w < floor:
            stubs.append((n, w))
    for n in notes_in(lib, "sources"):
        wiki_words += words(section(read(n), "Summary"))
        wiki_words += words(section(read(n), "Key takeaways"))

    raw_words = 0
    raw_dir = os.path.join(lib, "raw")
    if os.path.isdir(raw_dir):
        for base, dirs, files in os.walk(raw_dir):
            dirs[:] = [d for d in dirs if d != "assets"]
            for f in files:
                if f.endswith((".txt", ".md")) and f != "INDEX.md":
                    raw_words += words(read(os.path.join(base, f)))
    ratio = (raw_words / wiki_words) if wiki_words else 0.0
    return sorted(stubs), ratio


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="Lint compiled wiki notes for depth.")
    ap.add_argument("root", nargs="?", default=".", help="repo root or a library dir")
    ap.add_argument("--pair-threshold", type=float, default=0.85,
                    help="overlap coefficient that counts two notes as duplicates")
    ap.add_argument("--template-frac", type=float, default=0.3,
                    help="fraction of notes sharing a phrase that flags a template")
    ap.add_argument("--stub-floor", type=int, default=120,
                    help="concept body word count below which it is flagged a stub")
    ap.add_argument("--ratio-flag", type=float, default=12.0,
                    help="raw:wiki word ratio above which compression is flagged")
    ap.add_argument("--strict", action="store_true",
                    help="advisory findings also affect the exit code")
    args = ap.parse_args()

    root = os.path.normpath(args.root)
    gate_problems, advisory_flags = 0, 0

    for lib in libraries(root):
        name = os.path.basename(lib.rstrip("/")) or lib
        print(f"== {name} ==")

        templates, pairs = check_duplicates(lib, args.pair_threshold, args.template_frac)
        if templates or pairs:
            for phrase, labels in templates:
                gate_problems += len(labels)
                print(f"  [GATE] dup: templated phrase reused across {len(labels)} notes "
                      f'— likely boilerplate. Shared: "…{phrase}…"')
                for label in labels[:6]:
                    print(f"      {label}")
                if len(labels) > 6:
                    print(f"      … and {len(labels) - 6} more")
            for a, b in pairs:
                gate_problems += 1
                print(f"  [GATE] dup: near-duplicate pair:")
                print(f"      {a}")
                print(f"      {b}")
        else:
            print("  [GATE] dup: OK — no templated or near-duplicate summaries/leads.")

        echoes = check_echo(lib, args.pair_threshold)
        if echoes:
            gate_problems += len(echoes)
            print(f"  [GATE] echo: {len(echoes)} takeaway(s) restate a linked concept's lead:")
            for f, slug in echoes[:12]:
                print(f"      {f}  ->  {slug}")
            if len(echoes) > 12:
                print(f"      … and {len(echoes) - 12} more")
        else:
            print("  [GATE] echo: OK — takeaways are not concept-lead echoes.")

        stubs, ratio = check_depth(lib, args.stub_floor)
        flagged_ratio = ratio > args.ratio_flag
        advisory_flags += len(stubs) + (1 if flagged_ratio else 0)
        print(f"  [info] depth: raw:wiki word ratio {ratio:.0f}:1"
              f"{'  <-- review (thin compile?)' if flagged_ratio else ''}")
        if stubs:
            print(f"  [info] depth: {len(stubs)} concept body(ies) under {args.stub_floor} "
                  f"words (review — don't pad to clear this):")
            for f, w in stubs[:12]:
                print(f"      {f}  ({w} words)")
            if len(stubs) > 12:
                print(f"      … and {len(stubs) - 12} more")

    print()
    print(f"Gating problems: {gate_problems}.  Advisory flags: {advisory_flags}.")
    if args.strict:
        return 1 if (gate_problems or advisory_flags) else 0
    return 1 if gate_problems else 0


if __name__ == "__main__":
    sys.exit(main())

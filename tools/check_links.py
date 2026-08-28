#!/usr/bin/env python3
"""Lint the knowledge-base link graph.

Reproducible health-check helper for the `kb` repo. Catches the classes of
breakage the manual audits have missed — over-encoded relative links, links to
unicode filenames, dangling references — by resolving every markdown link the
way GitHub and editors actually do.

Audits
------
- **links**   (always)   broken relative-path links (the core check)
- **orphans** (--orphans) concept/source notes with no inbound wiki reference
- **front**   (--front)   wiki notes missing YAML frontmatter

Why a script: the 2026-05-28 health check declared the link graph "clean" while
three source notes had broken raw-file links, because the ad-hoc check did not
URL-decode `%27` (a straight apostrophe) against filenames containing a curly
apostrophe `’`. This resolver decodes percent-escapes, honours
`<angle-bracket>` destinations, and only treats a trailing `#fragment` as an
anchor when the literal path (fragment included) does not exist on disk — so a
file literally named `...#1 Rule....txt` still resolves.

Usage
-----
    python3 tools/check_links.py                 # whole repo, links audit
    python3 tools/check_links.py self-improvement # one library
    python3 tools/check_links.py --orphans --front

Exit code is non-zero if any audit finds problems, so it can gate CI or a
SessionStart hook.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from urllib.parse import unquote

# Files that intentionally contain template placeholders like `../concepts/x.md`
# or `<slug>.md` — not real links, so skip them in the links audit.
SKIP_FILES = {"protocol.md", "library.md"}

# `[text](dest)` and `![alt](dest)`, where dest is either <bracketed> or bare.
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^)\s]+)")

# Notes whose link destinations point at deliberately-absent binaries. The note
# body documents the absence (e.g. "binary not yet stored"); don't flag these.
KNOWN_PLACEHOLDER_MARKERS = ("binary not yet stored",)


def repo_md_files(root: str) -> list[str]:
    out = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            if f.endswith(".md"):
                out.append(os.path.join(base, f))
    return sorted(out)


def iter_links(text: str):
    """Yield (line_number, raw_destination) for every markdown link."""
    for i, line in enumerate(text.splitlines(), 1):
        for m in LINK_RE.finditer(line):
            yield i, m.group(1).strip()


def resolves(dest: str, base_dir: str) -> bool:
    """True if a relative destination points at something on disk."""
    if dest.startswith("<") and dest.endswith(">"):
        dest = dest[1:-1].strip()
    if dest.startswith(("http://", "https://", "mailto:", "#")):
        return True  # external or pure in-page anchor — not our concern
    decoded = unquote(dest)
    # Try the literal path first (handles filenames containing '#').
    full = os.path.normpath(os.path.join(base_dir, decoded))
    if os.path.exists(full):
        return True
    # Otherwise treat a trailing #fragment as a heading anchor.
    if "#" in decoded:
        path = decoded.split("#", 1)[0]
        if not path:
            return True
        return os.path.exists(os.path.normpath(os.path.join(base_dir, path)))
    return False


def audit_links(files: list[str]) -> list[tuple[str, int, str]]:
    broken = []
    for f in files:
        if os.path.basename(f) in SKIP_FILES:
            continue
        text = open(f, encoding="utf-8").read()
        is_placeholder = any(m in text for m in KNOWN_PLACEHOLDER_MARKERS)
        for line_no, dest in iter_links(text):
            if resolves(dest, os.path.dirname(f)):
                continue
            if is_placeholder:
                continue  # documented intentional absence
            broken.append((f, line_no, dest))
    return broken


def audit_orphans(root: str) -> list[str]:
    """Concept/source notes referenced by nothing else in their library."""
    orphans = []
    for lib in sorted(_libraries(root)):
        notes = []
        for sub in ("concepts", "sources"):
            d = os.path.join(lib, "wiki", sub)
            if os.path.isdir(d):
                notes += [
                    os.path.join(d, n)
                    for n in os.listdir(d)
                    if n.endswith(".md") and n != "README.md"
                ]
        corpus = {}
        for base, dirs, files in os.walk(lib):
            dirs[:] = [d for d in dirs if d != ".git"]
            for f in files:
                if f.endswith(".md"):
                    p = os.path.join(base, f)
                    corpus[p] = open(p, encoding="utf-8").read()
        for note in notes:
            name = os.path.basename(note)
            if not any(p != note and name in txt for p, txt in corpus.items()):
                orphans.append(note)
    return orphans


def audit_frontmatter(root: str) -> list[str]:
    missing = []
    for lib in sorted(_libraries(root)):
        wiki = os.path.join(lib, "wiki")
        if not os.path.isdir(wiki):
            continue
        for base, dirs, files in os.walk(wiki):
            dirs[:] = [d for d in dirs if d != ".git"]
            for f in files:
                if not f.endswith(".md") or f in ("README.md", "INDEX.md"):
                    continue
                p = os.path.join(base, f)
                if not open(p, encoding="utf-8").read().startswith("---"):
                    missing.append(p)
    return missing


def _libraries(root: str) -> list[str]:
    """Dirs that look like managed libraries (have a wiki/).

    Handles both being pointed at the repo root (scan child libraries) and at a
    single library dir (scan it directly).
    """
    if os.path.isdir(os.path.join(root, "wiki")):
        return [root]
    out = []
    for n in os.listdir(root):
        p = os.path.join(root, n)
        if os.path.isdir(p) and os.path.isdir(os.path.join(p, "wiki")):
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint the kb link graph.")
    ap.add_argument("root", nargs="?", default=".", help="repo root or a library dir")
    ap.add_argument("--orphans", action="store_true", help="also report orphan notes")
    ap.add_argument("--front", action="store_true", help="also report missing frontmatter")
    args = ap.parse_args()

    root = os.path.normpath(args.root)
    files = repo_md_files(root)
    problems = 0

    broken = audit_links(files)
    print(f"Links: scanned {len(files)} markdown files.")
    if broken:
        problems += len(broken)
        print(f"  BROKEN ({len(broken)}):")
        for f, line, dest in broken:
            print(f"    {f}:{line}  ->  {dest}")
    else:
        print("  OK — no broken relative links.")

    if args.orphans:
        orphans = audit_orphans(root)
        print(f"Orphans: {len(orphans)} note(s) with no inbound reference.")
        for o in orphans:
            problems += 1
            print(f"    {o}")

    if args.front:
        missing = audit_frontmatter(root)
        print(f"Frontmatter: {len(missing)} wiki note(s) missing YAML frontmatter.")
        for m in missing:
            problems += 1
            print(f"    {m}")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

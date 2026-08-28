# Maintenance and research tools

Funes includes two dependency-free Python linters for repository health checks,
a PDF text-extraction helper, and an optional targeted transcript helper.

## `check_links.py` — link-graph lint

This is the reproducible backbone of the [Librarian Protocol](../protocol.md)
health check. It resolves Markdown links after URL-decoding destinations and
normalizing Unicode, which catches filename mismatches that visual inspection
can miss. Links inside fenced code examples are ignored.

```bash
python3 tools/check_links.py                     # audit every library
python3 tools/check_links.py starter-library     # audit one library
python3 tools/check_links.py --orphans --front   # include graph + metadata checks
```

The always-on audit reports broken relative links. `--orphans` reports concept
and source notes without an inbound link in their library, and `--front` reports
wiki notes without YAML frontmatter. Any finding produces a non-zero exit code.

`protocol.md` and `library.md` are skipped because they contain literal template
placeholders. Raw notes that explicitly document a missing binary are also
excluded from broken-link findings.

## `compile_lint.py` — compile-depth lint

This checks whether compilation extracted source-specific substance instead of
only producing well-linked files.

```bash
python3 tools/compile_lint.py                  # every library
python3 tools/compile_lint.py starter-library  # one library
python3 tools/compile_lint.py --strict         # advisories also fail
```

The linter has two deliberately different tiers:

- **Gates:** repeated template prose, near-duplicate summaries or leads, and
  takeaways that simply echo a linked concept's lead sentence.
- **Advisories:** short concept bodies and high raw-to-wiki compression ratios.
  These are review prompts, not writing targets; investigate them rather than
  padding prose to clear a threshold.

The tool intentionally does not use string matching as a factual-grounding gate.
OCR and speech-to-text errors make that unreliable, while the incentive can
encourage deletion of useful detail. Fidelity review remains an editorial step
that reads the source and compiled note together.

Both linters run in [GitHub Actions](../.github/workflows/funes-lint.yml) on
every push and pull request.

## `pdf_text.py` — PDF text extraction with OCR fallback

This creates a searchable text edition beside a PDF without modifying the
authoritative binary. It tries each page's native text layer first, then renders
and OCRs only pages whose native layer is missing or too sparse.

```bash
python3 tools/pdf_text.py library/raw/document.pdf
python3 tools/pdf_text.py library/raw/document.pdf --pages 1-20,35-
python3 tools/pdf_text.py library/raw/document.pdf --ocr-all --dpi 220
```

Output defaults to the PDF's path with a `.txt` suffix. Each page is labeled as
`native text`, `OCR`, or `extraction failed`, and the header records extraction
settings and tool versions. The default 60-second timeout applies to each
external command, preventing a pathological page from stalling the entire run.
Successful pages are still written if another page fails; the command exits
non-zero when any page failed. Use `--fail-fast` when partial output is unwanted.

The Python wrapper has no package dependencies, but PDF/OCR work uses
[Poppler](https://poppler.freedesktop.org/) (`pdfinfo`, `pdftotext`,
`pdftoppm`) and [Tesseract](https://github.com/tesseract-ocr/tesseract):

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils tesseract-ocr

# macOS with Homebrew
brew install poppler tesseract
```

OCR is machine-generated. Verify quotations, names, numbers, tables, and other
critical readings against the PDF page images. Dense schematics and unusual
layouts often need manual review or different Tesseract `--psm` settings.

## `youtube_transcript.py` — targeted transcript retrieval

This best-effort helper accepts a specific public YouTube URL or video ID,
prefers manually created captions, and can emit plain text, JSON, SRT, or
WebVTT. Install its narrow optional dependency before use:

```bash
python3 -m pip install -r tools/requirements-youtube.txt
```

Examples:

```bash
python3 tools/youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
python3 tools/youtube_transcript.py VIDEO_ID --timestamps
python3 tools/youtube_transcript.py VIDEO_ID --format json -o /tmp/transcript.json
python3 tools/youtube_transcript.py VIDEO_ID --list
python3 tools/youtube_transcript.py VIDEO_ID --languages en,en-US
python3 tools/youtube_transcript.py VIDEO_ID --manual-only
```

Use it for targeted research, not bulk channel scraping. Auto-generated
captions are noisy, so verify names, dates, quotations, and substantive claims
against stronger sources. Do not reproduce long copyrighted passages.

The helper relies on an undocumented YouTube web endpoint through
`youtube-transcript-api`; upstream changes or cloud-IP blocking can make it fail.
It reports those failures clearly and does not attempt identity rotation.

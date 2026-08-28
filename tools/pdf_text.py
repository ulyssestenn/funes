#!/usr/bin/env python3
"""Extract searchable text from PDFs, with page-level OCR fallback.

The PDF remains the authoritative raw source. This helper writes a sibling text
edition that records whether each page came from the native text layer or OCR.

External commands:
  - Poppler: pdfinfo, pdftotext, pdftoppm
  - Tesseract: tesseract (only needed when OCR is used)
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class ExtractionError(RuntimeError):
    """A recoverable page or dependency error."""


def run_command(command: list[str], timeout: float) -> str:
    """Run a UTF-8 command and return stdout, raising a concise error."""
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise ExtractionError(f"required command not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ExtractionError(
            f"{command[0]} timed out after {timeout:g}s"
        ) from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        message = detail[-1] if detail else f"exit code {completed.returncode}"
        raise ExtractionError(f"{command[0]} failed: {message}")
    return completed.stdout


def page_count(pdf: Path, timeout: float) -> int:
    output = run_command(["pdfinfo", str(pdf)], timeout)
    match = re.search(r"^Pages:\s+(\d+)\s*$", output, flags=re.MULTILINE)
    if not match:
        raise ExtractionError("pdfinfo did not report a page count")
    return int(match.group(1))


def parse_pages(spec: str | None, total: int) -> list[int]:
    """Parse a 1-based page expression such as 1-3,7,10-."""
    if spec is None:
        return list(range(1, total + 1))

    pages: set[int] = set()
    for item in spec.split(","):
        token = item.strip()
        if not token:
            raise argparse.ArgumentTypeError("empty item in --pages")
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            if not start_text and not end_text:
                raise argparse.ArgumentTypeError("page range cannot be '-' only")
            start = int(start_text) if start_text else 1
            end = int(end_text) if end_text else total
            if start > end:
                raise argparse.ArgumentTypeError(
                    f"page range starts after it ends: {token}"
                )
            pages.update(range(start, end + 1))
        else:
            pages.add(int(token))

    invalid = sorted(page for page in pages if page < 1 or page > total)
    if invalid:
        raise argparse.ArgumentTypeError(
            f"pages outside 1-{total}: {', '.join(map(str, invalid))}"
        )
    return sorted(pages)


def useful_characters(text: str) -> int:
    """Count letters and numbers, ignoring layout noise and punctuation."""
    return sum(character.isalnum() for character in text)


def native_text(pdf: Path, page: int, timeout: float) -> str:
    return run_command(
        [
            "pdftotext",
            "-f",
            str(page),
            "-l",
            str(page),
            "-layout",
            "-enc",
            "UTF-8",
            str(pdf),
            "-",
        ],
        timeout,
    ).strip("\f\n")


def ocr_text(
    pdf: Path,
    page: int,
    work_dir: Path,
    dpi: int,
    language: str,
    psm: int,
    timeout: float,
) -> str:
    prefix = work_dir / f"page-{page:06d}"
    run_command(
        [
            "pdftoppm",
            "-f",
            str(page),
            "-l",
            str(page),
            "-singlefile",
            "-r",
            str(dpi),
            "-png",
            str(pdf),
            str(prefix),
        ],
        timeout,
    )
    image = prefix.with_suffix(".png")
    if not image.exists():
        raise ExtractionError("pdftoppm did not create the expected page image")
    try:
        return run_command(
            [
                "tesseract",
                str(image),
                "stdout",
                "-l",
                language,
                "--psm",
                str(psm),
                "-c",
                "preserve_interword_spaces=1",
            ],
            timeout,
        ).strip()
    finally:
        image.unlink(missing_ok=True)


def command_version(command: str) -> str | None:
    if shutil.which(command) is None:
        return None
    try:
        output = subprocess.run(
            [command, "--version"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return command
    first_line = output.strip().splitlines()
    return first_line[0] if first_line else command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extract a PDF's native text page by page and use OCR where the "
            "native layer is missing or too sparse."
        )
    )
    parser.add_argument("pdf", type=Path, help="input PDF")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output text path (default: PDF path with a .txt suffix)",
    )
    parser.add_argument(
        "--pages",
        help="1-based pages/ranges, for example 1-3,7,10- (default: all)",
    )
    parser.add_argument(
        "--min-native-chars",
        type=int,
        default=40,
        metavar="N",
        help="OCR pages with fewer than N alphanumeric native characters (default: 40)",
    )
    parser.add_argument(
        "--ocr-all",
        action="store_true",
        help="OCR every selected page instead of trying native text first",
    )
    parser.add_argument("--dpi", type=int, default=220, help="OCR render DPI (default: 220)")
    parser.add_argument(
        "--language",
        default="eng",
        help="Tesseract language code(s), such as eng or eng+deu (default: eng)",
    )
    parser.add_argument(
        "--psm",
        type=int,
        default=3,
        help="Tesseract page segmentation mode (default: 3, automatic)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        metavar="SECONDS",
        help="timeout for each external command (default: 60)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="stop at the first page error instead of preserving partial results",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing output file",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="omit the extraction provenance header",
    )
    return parser


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if not args.pdf.is_file():
        parser.error(f"input does not exist or is not a file: {args.pdf}")
    if args.pdf.suffix.lower() != ".pdf":
        parser.error(f"input does not have a .pdf suffix: {args.pdf}")
    if args.output == args.pdf:
        parser.error("output must not overwrite the source PDF")
    if args.output.exists() and not args.force:
        parser.error(f"output already exists (use --force): {args.output}")
    if args.min_native_chars < 0:
        parser.error("--min-native-chars must be non-negative")
    if args.dpi < 72:
        parser.error("--dpi must be at least 72")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not 0 <= args.psm <= 13:
        parser.error("--psm must be between 0 and 13")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output = args.output or args.pdf.with_suffix(".txt")
    validate_args(args, parser)

    try:
        total_pages = page_count(args.pdf, args.timeout)
        selected_pages = parse_pages(args.pages, total_pages)
    except (ExtractionError, argparse.ArgumentTypeError, ValueError) as exc:
        parser.error(str(exc))

    sections: list[str] = []
    failures: list[tuple[int, str]] = []
    native_pages = 0
    ocr_pages = 0

    with tempfile.TemporaryDirectory(prefix="funes-pdf-text-") as temp_name:
        work_dir = Path(temp_name)
        for page in selected_pages:
            method = "OCR"
            try:
                text = ""
                native_error: ExtractionError | None = None
                if not args.ocr_all:
                    try:
                        text = native_text(args.pdf, page, args.timeout)
                    except ExtractionError as exc:
                        native_error = exc
                    if useful_characters(text) >= args.min_native_chars:
                        method = "native text"
                        native_pages += 1
                    else:
                        text = ocr_text(
                            args.pdf,
                            page,
                            work_dir,
                            args.dpi,
                            args.language,
                            args.psm,
                            args.timeout,
                        )
                        ocr_pages += 1
                else:
                    text = ocr_text(
                        args.pdf,
                        page,
                        work_dir,
                        args.dpi,
                        args.language,
                        args.psm,
                        args.timeout,
                    )
                    ocr_pages += 1

                if not text.strip():
                    detail = "OCR returned no text"
                    if native_error is not None:
                        detail += f" after native extraction failed ({native_error})"
                    raise ExtractionError(detail)
                sections.append(f"===== PAGE {page} ({method}) =====\n{text.strip()}")
                print(f"page {page}/{total_pages}: {method}", file=sys.stderr)
            except ExtractionError as exc:
                failures.append((page, str(exc)))
                sections.append(f"===== PAGE {page} (extraction failed) =====\n[{exc}]")
                print(f"page {page}/{total_pages}: ERROR: {exc}", file=sys.stderr)
                if args.fail_fast:
                    break

    header: list[str] = []
    if not args.no_header:
        versions = [
            version
            for version in (command_version("pdftotext"), command_version("tesseract"))
            if version
        ]
        header = [
            f"{args.pdf.stem} - extracted text edition",
            f"Source: {args.pdf.name}",
            f"Generated: {dt.date.today().isoformat()}",
            (
                "Method: page-level native text with OCR fallback "
                f"(minimum {args.min_native_chars} alphanumeric characters; {args.dpi} dpi)"
                if not args.ocr_all
                else f"Method: OCR for every selected page ({args.dpi} dpi)"
            ),
            "Tools: " + ("; ".join(versions) if versions else "versions unavailable"),
            "Machine-generated text; verify critical readings against the PDF.",
        ]

    output_text = "\n".join(header + ([""] if header else []) + sections).rstrip() + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output_text, encoding="utf-8")

    print(
        f"wrote {args.output} ({native_pages} native, {ocr_pages} OCR, "
        f"{len(failures)} failed page(s))",
        file=sys.stderr,
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

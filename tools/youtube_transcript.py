#!/usr/bin/env python3
"""Fetch a public YouTube transcript for Funes research.

Requires: youtube-transcript-api>=1.2.4,<2
Run from repo root:
    python3 tools/youtube_transcript.py VIDEO_OR_URL
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(value: str) -> str:
    """Accept a YouTube video ID or common YouTube URL forms."""
    value = value.strip()
    if VIDEO_ID_RE.fullmatch(value):
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    if host.startswith("m."):
        host = host[2:]

    if host == "youtu.be":
        candidate = parsed.path.strip("/").split("/")[0]
        if VIDEO_ID_RE.fullmatch(candidate):
            return candidate

    if host in {"youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
            if VIDEO_ID_RE.fullmatch(candidate):
                return candidate
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
            candidate = parts[1]
            if VIDEO_ID_RE.fullmatch(candidate):
                return candidate

    raise ValueError(
        "Expected an 11-character YouTube video ID or a standard "
        "youtube.com / youtu.be video URL."
    )


def parse_languages(value: str) -> list[str]:
    langs = [part.strip() for part in value.split(",") if part.strip()]
    if not langs:
        raise argparse.ArgumentTypeError("provide at least one language code")
    return langs


def fmt_timestamp(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch captions/transcripts for one public YouTube video. "
            "Manual captions are preferred by default, then auto-generated captions."
        )
    )
    parser.add_argument("video", help="YouTube video URL or 11-character video ID")
    parser.add_argument(
        "--languages",
        type=parse_languages,
        default=["en"],
        metavar="CODES",
        help="comma-separated language codes in preference order (default: en)",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--manual-only",
        action="store_true",
        help="require manually created captions",
    )
    source.add_argument(
        "--generated-only",
        action="store_true",
        help="require automatically generated captions",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_only",
        help="list available transcript tracks instead of fetching one",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "srt", "vtt"),
        default="text",
        help="output format (default: text)",
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="prefix each line of text output with its start timestamp",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write output to a file instead of stdout",
    )
    return parser


def load_api():
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api.formatters import SRTFormatter, WebVTTFormatter
    except ImportError as exc:
        print(
            "youtube-transcript-api is not installed.\n"
            "Install the Funes's optional YouTube dependency with:\n"
            "  python3 -m pip install -r tools/requirements-youtube.txt",
            file=sys.stderr,
        )
        raise SystemExit(3) from exc
    return YouTubeTranscriptApi, SRTFormatter, WebVTTFormatter


def write_output(text: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(text)
        if text and not text.endswith("\n"):
            sys.stdout.write("\n")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        video_id = extract_video_id(args.video)
    except ValueError as exc:
        parser.error(str(exc))

    YouTubeTranscriptApi, SRTFormatter, WebVTTFormatter = load_api()
    api = YouTubeTranscriptApi()

    try:
        transcript_list = api.list(video_id)

        if args.list_only:
            rows = []
            for track in transcript_list:
                rows.append(
                    {
                        "video_id": track.video_id,
                        "language": track.language,
                        "language_code": track.language_code,
                        "generated": bool(track.is_generated),
                        "translatable": bool(track.is_translatable),
                    }
                )
            write_output(json.dumps(rows, ensure_ascii=False, indent=2), args.output)
            return 0

        if args.manual_only:
            track = transcript_list.find_manually_created_transcript(args.languages)
        elif args.generated_only:
            track = transcript_list.find_generated_transcript(args.languages)
        else:
            track = transcript_list.find_transcript(args.languages)

        transcript = track.fetch()

        if args.format == "json":
            payload = {
                "video_id": transcript.video_id,
                "language": transcript.language,
                "language_code": transcript.language_code,
                "generated": bool(transcript.is_generated),
                "snippets": transcript.to_raw_data(),
            }
            rendered = json.dumps(payload, ensure_ascii=False, indent=2)
        elif args.format == "srt":
            rendered = SRTFormatter().format_transcript(transcript)
        elif args.format == "vtt":
            rendered = WebVTTFormatter().format_transcript(transcript)
        else:
            lines = []
            for snippet in transcript:
                text = " ".join(snippet.text.split())
                if not text:
                    continue
                if args.timestamps:
                    lines.append(f"[{fmt_timestamp(snippet.start)}] {text}")
                else:
                    lines.append(text)
            rendered = "\n".join(lines)

        write_output(rendered, args.output)
        print(
            f"video={video_id} language={transcript.language_code} "
            f"generated={str(bool(transcript.is_generated)).lower()} "
            f"snippets={len(transcript)}",
            file=sys.stderr,
        )
        return 0

    except Exception as exc:
        name = type(exc).__name__
        print(f"{name}: {exc}", file=sys.stderr)
        if name in {"RequestBlocked", "IpBlocked"}:
            print(
                "YouTube may be blocking this network. Try the same command from a "
                "normal local connection, or use another permitted research route.",
                file=sys.stderr,
            )
        return 4


if __name__ == "__main__":
    raise SystemExit(main())

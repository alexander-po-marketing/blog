from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from .cleaners import strip_divi_meta
from .divi_shortcodes import extract_divi_html
from .html_to_blocks import html_to_blocks
from .report import PostReport, write_report
from .wxr import WXRParseError, parse_wxr, update_post_content, write_wxr


def _write_debug(slug: str, html: str, blocks: str, output_dir: Path) -> None:
    html_dir = output_dir / "html"
    blocks_dir = output_dir / "blocks"
    html_dir.mkdir(parents=True, exist_ok=True)
    blocks_dir.mkdir(parents=True, exist_ok=True)
    (html_dir / f"{slug}.html").write_text(html, encoding="utf-8")
    (blocks_dir / f"{slug}.html").write_text(blocks, encoding="utf-8")


def convert(input_path: Path, output_path: Path, strip_meta: bool, dump_debug: bool) -> int:
    try:
        doc = parse_wxr(input_path)
    except WXRParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    reports: list[PostReport] = []

    for post in doc.posts:
        source_html = post.content_el.text or ""
        combined_html, counts = extract_divi_html(source_html)
        blocks = html_to_blocks(combined_html, doc.attachment_map)
        update_post_content(post, blocks)
        if strip_meta:
            strip_divi_meta(post.element)
        reports.append(
            PostReport(
                post_id=post.post_id,
                slug=post.slug or f"post-{post.post_id}",
                title=post.title,
                shortcode_counts=dict(counts),
            )
        )
        if dump_debug:
            _write_debug(reports[-1].slug, combined_html, blocks, output_path.parent / "out")

    write_wxr(doc, output_path)

    if dump_debug:
        report_path = output_path.parent / "out" / "report.csv"
        write_report(report_path, reports)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert Divi WXR exports to Gutenberg block WXR.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="Convert a WXR file.")
    convert_parser.add_argument("--input", required=True, type=Path)
    convert_parser.add_argument("--output", required=True, type=Path)
    convert_parser.add_argument(
        "--strip-divi-meta",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Remove Divi-related postmeta entries.",
    )
    convert_parser.add_argument(
        "--dump-debug",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Write per-post debug HTML and a report CSV.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "convert":
        sys.exit(convert(args.input, args.output, args.strip_divi_meta, args.dump_debug))


if __name__ == "__main__":
    main()

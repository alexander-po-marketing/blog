# divi2gutenberg

Convert WordPress WXR exports that contain Divi Builder shortcodes into clean Gutenberg (Block Editor)
markup ready for Blocksy or any Gutenberg-based theme.

## Features

- Parses WXR exports and preserves namespaces/content.
- Extracts HTML content from Divi shortcodes such as `et_pb_text`, `et_pb_code`, and
  `et_pb_team_member` while ignoring structural wrappers.
- Converts HTML to Gutenberg blocks with sensible fallbacks to `wp:html` blocks.
- Optional cleanup of Divi-related postmeta.
- Debug output: per-post HTML, Gutenberg blocks, and a CSV conversion report.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
divi2gutenberg convert --input input.xml --output output.xml
```

Options:

- `--strip-divi-meta/--no-strip-divi-meta` (default: strip)
- `--dump-debug/--no-dump-debug`

When `--dump-debug` is enabled, the converter writes:

- `out/html/<slug>.html` (combined Divi HTML)
- `out/blocks/<slug>.html` (Gutenberg blocks)
- `out/report.csv` (conversion stats)

## Development

```bash
pip install -e .[dev]
pytest
```

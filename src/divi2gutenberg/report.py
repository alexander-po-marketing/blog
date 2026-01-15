from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class PostReport:
    post_id: str
    slug: str
    title: str
    shortcode_counts: dict[str, int]


def write_report(path: Path, reports: Iterable[PostReport]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["post_id", "slug", "title", "shortcodes"])
        for report in reports:
            counts = ";".join(f"{name}:{count}" for name, count in report.shortcode_counts.items())
            writer.writerow([report.post_id, report.slug, report.title, counts])

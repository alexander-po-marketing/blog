from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, List, Union


SHORTCODE_RE = re.compile(r"\[(\/?)\s*([a-zA-Z0-9_]+)([^\]]*)\]")
SELF_CLOSING = {"et_pb_line_break_holder"}
CONTENT_SHORTCODES = {"et_pb_text", "et_pb_code", "et_pb_team_member"}
CONTAINER_SHORTCODES = {"et_pb_section", "et_pb_row", "et_pb_column"}


@dataclass
class ShortcodeNode:
    name: str
    attrs: str
    parts: List[Union[str, "ShortcodeNode"]] = field(default_factory=list)

    def body_html(self) -> str:
        return "".join(
            part if isinstance(part, str) else part.to_html() for part in self.parts
        )

    def to_html(self) -> str:
        return self.body_html()


ParsedPart = Union[str, ShortcodeNode]


def parse_shortcodes(text: str) -> List[ParsedPart]:
    root: List[ParsedPart] = []
    stack: List[ShortcodeNode] = []
    pos = 0

    def append_part(part: ParsedPart) -> None:
        if stack:
            stack[-1].parts.append(part)
        else:
            root.append(part)

    for match in SHORTCODE_RE.finditer(text):
        start, end = match.span()
        if start > pos:
            append_part(text[pos:start])
        is_closing = match.group(1) == "/"
        name = match.group(2)
        attrs = match.group(3).strip()

        if not is_closing:
            if name in SELF_CLOSING:
                append_part(ShortcodeNode(name=name, attrs=attrs, parts=[]))
            else:
                node = ShortcodeNode(name=name, attrs=attrs)
                append_part(node)
                stack.append(node)
        else:
            if stack and stack[-1].name == name:
                stack.pop()
            else:
                append_part(match.group(0))
        pos = end

    if pos < len(text):
        append_part(text[pos:])

    return root


def _extract_from_parts(parts: Iterable[ParsedPart], counter: Counter[str]) -> str:
    output: List[str] = []
    for part in parts:
        if isinstance(part, str):
            output.append(part)
            continue
        counter[part.name] += 1
        if part.name in SELF_CLOSING:
            output.append("<br/>")
            continue
        if part.name in CONTENT_SHORTCODES:
            output.append(part.body_html())
            continue
        if part.name in CONTAINER_SHORTCODES:
            output.append(_extract_from_parts(part.parts, counter))
            continue
        body = part.body_html()
        if body.strip():
            output.append(body)
    return "".join(output)


def extract_divi_html(text: str) -> tuple[str, Counter[str]]:
    counter: Counter[str] = Counter()
    parts = parse_shortcodes(text)
    html = _extract_from_parts(parts, counter)
    html = re.sub(r"\n{3,}", "\n\n", html).strip()
    return html, counter

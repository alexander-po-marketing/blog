from __future__ import annotations

from typing import Iterable

from bs4 import BeautifulSoup, NavigableString, Tag


BLOCK_WRAPPERS = {"div", "section", "span"}


def _block(block_name: str, inner_html: str, attrs: str | None = None) -> str:
    attr_text = f" {attrs}" if attrs else ""
    return f"<!-- wp:{block_name}{attr_text} -->\n{inner_html}\n<!-- /wp:{block_name} -->"


def _paragraph(text: str) -> str:
    return _block("paragraph", f"<p>{text}</p>")


def _heading(tag: Tag) -> str:
    level = int(tag.name[1])
    return _block("heading", str(tag), attrs=f'{{"level":{level}}}')


def _list(tag: Tag) -> str:
    return _block("list", str(tag))


def _separator() -> str:
    return _block("separator", "<hr/>")


def _code(tag: Tag) -> str:
    if tag.name == "pre":
        inner = str(tag)
    else:
        inner = f"<pre><code>{tag.get_text()}</code></pre>"
    return _block("code", inner)


def _quote(tag: Tag) -> str:
    return _block("quote", str(tag))


def _image_block(tag: Tag, attachment_id: int | None) -> str | None:
    img = tag if tag.name == "img" else tag.find("img")
    if img is None:
        return None
    src = img.get("src")
    if attachment_id is None:
        return None
    img_html = str(img)
    figure = f"<figure class=\"wp-block-image\">{img_html}</figure>"
    return _block("image", figure, attrs=f'{{"id":{attachment_id}}}')


def _html_block(html: str) -> str:
    return _block("html", html)


def _attachment_id_for_tag(tag: Tag, attachment_map: dict[str, int]) -> int | None:
    img = tag if tag.name == "img" else tag.find("img")
    if img is None:
        return None
    src = img.get("src")
    if not src:
        return None
    return attachment_map.get(src)


def _process_nodes(nodes: Iterable, attachment_map: dict[str, int]) -> list[str]:
    blocks: list[str] = []
    for node in nodes:
        if isinstance(node, NavigableString):
            text = str(node).strip()
            if text:
                blocks.append(_paragraph(text))
            continue
        if not isinstance(node, Tag):
            continue
        tag_name = node.name.lower()
        if tag_name in {"p"}:
            blocks.append(_block("paragraph", str(node)))
        elif tag_name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            blocks.append(_heading(node))
        elif tag_name in {"ul", "ol"}:
            blocks.append(_list(node))
        elif tag_name == "hr":
            blocks.append(_separator())
        elif tag_name in {"pre", "code"}:
            blocks.append(_code(node))
        elif tag_name == "blockquote":
            blocks.append(_quote(node))
        elif tag_name in {"figure", "img"}:
            attachment_id = _attachment_id_for_tag(node, attachment_map)
            image_block = _image_block(node, attachment_id)
            if image_block:
                blocks.append(image_block)
            else:
                blocks.append(_html_block(str(node)))
        elif tag_name in BLOCK_WRAPPERS and not node.attrs:
            blocks.extend(_process_nodes(node.children, attachment_map))
        else:
            blocks.append(_html_block(str(node)))
    return blocks


def html_to_blocks(html: str, attachment_map: dict[str, int]) -> str:
    soup = BeautifulSoup(html, "html.parser")
    nodes = soup.body.children if soup.body else soup.contents
    blocks = _process_nodes(nodes, attachment_map)
    return "\n\n".join(blocks).strip()

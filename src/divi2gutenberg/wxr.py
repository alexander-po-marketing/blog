from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


NAMESPACES = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    "wp": "http://wordpress.org/export/1.2/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


@dataclass
class PostItem:
    element: ET.Element
    post_id: str
    title: str
    slug: str
    status: str
    content_el: ET.Element


@dataclass
class WXRDocument:
    tree: ET.ElementTree
    channel: ET.Element
    posts: list[PostItem]
    attachment_map: dict[str, int]


class WXRParseError(ValueError):
    pass


def _register_namespaces() -> None:
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)


def parse_wxr(path: Path) -> WXRDocument:
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise WXRParseError(f"Invalid XML: {exc}") from exc

    root = tree.getroot()
    channel = root.find("channel")
    if channel is None:
        raise WXRParseError("Missing channel element in WXR file.")

    posts: list[PostItem] = []
    attachment_map: dict[str, int] = {}

    for item in channel.findall("item"):
        post_type_el = item.find("wp:post_type", NAMESPACES)
        post_type = post_type_el.text if post_type_el is not None else ""
        post_id_el = item.find("wp:post_id", NAMESPACES)
        post_id = post_id_el.text if post_id_el is not None else ""

        if post_type == "attachment":
            guid_el = item.find("guid")
            guid = guid_el.text if guid_el is not None else None
            attachment_url_el = item.find("wp:attachment_url", NAMESPACES)
            attachment_url = attachment_url_el.text if attachment_url_el is not None else None
            if guid:
                attachment_map[guid] = int(post_id) if post_id.isdigit() else -1
            if attachment_url:
                attachment_map[attachment_url] = int(post_id) if post_id.isdigit() else -1
            continue

        if post_type != "post":
            continue

        title_el = item.find("title")
        title = title_el.text if title_el is not None else ""
        slug_el = item.find("wp:post_name", NAMESPACES)
        slug = slug_el.text if slug_el is not None else ""
        status_el = item.find("wp:status", NAMESPACES)
        status = status_el.text if status_el is not None else ""
        content_el = item.find("content:encoded", NAMESPACES)
        if content_el is None:
            raise WXRParseError("Missing content:encoded element in post item.")

        posts.append(
            PostItem(
                element=item,
                post_id=post_id,
                title=title,
                slug=slug,
                status=status,
                content_el=content_el,
            )
        )

    return WXRDocument(tree=tree, channel=channel, posts=posts, attachment_map=attachment_map)


def update_post_content(post: PostItem, new_html: str) -> None:
    if hasattr(ET, "CDATA"):
        post.content_el.text = ET.CDATA(new_html)
    else:
        post.content_el.text = new_html


def write_wxr(doc: WXRDocument, path: Path) -> None:
    _register_namespaces()
    doc.tree.write(path, encoding="utf-8", xml_declaration=True)

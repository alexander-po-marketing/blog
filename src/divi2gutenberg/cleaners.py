from __future__ import annotations

from xml.etree import ElementTree as ET


WP_NS = "http://wordpress.org/export/1.2/"


def strip_divi_meta(item: ET.Element) -> int:
    removed = 0
    for meta in list(item.findall(f"{{{WP_NS}}}postmeta")):
        key_el = meta.find(f"{{{WP_NS}}}meta_key")
        key = key_el.text if key_el is not None else ""
        if key.startswith("_et_") or "et_pb" in key:
            item.remove(meta)
            removed += 1
    return removed

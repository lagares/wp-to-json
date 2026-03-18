import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

NS = {
    "wp": "http://wordpress.org/export/1.0/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}


def parse_wordpress_xml(xml_path: Path) -> dict[str, Any]:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    channel = root.find("channel")
    if channel is None:
        raise ValueError("Invalid WordPress XML: missing channel element")

    result = {
        "title": get_text(channel, "title"),
        "link": get_text(channel, "link"),
        "description": get_text(channel, "description"),
        "language": get_text(channel, "language"),
        "posts": [],
    }

    for item in channel.findall("item"):
        post_type = get_text(item, "wp:post_type", NS)
        if post_type == "post":
            result["posts"].append(parse_post(item))

    return result


def parse_post(item: ET.Element) -> dict[str, Any]:
    categories = []
    for cat in item.findall("category"):
        categories.append(get_text(cat, None) or cat.text)

    return {
        "title": get_text(item, "title"),
        "link": get_text(item, "link"),
        "pub_date": get_text(item, "pubDate"),
        "content": get_text(item, "content:encoded", NS) or get_text(item, "content"),
        "excerpt": get_text(item, "excerpt:encoded", NS) or get_text(item, "excerpt"),
        "slug": get_text(item, "wp:post_name", NS),
        "status": get_text(item, "wp:status", NS),
        "date": get_text(item, "wp:post_date", NS),
        "modified": get_text(item, "wp:post_modified", NS),
        "id": get_text(item, "wp:post_id", NS),
        "categories": [c for c in categories if c],
        "tags": [
            get_text(t, None) or t.text
            for t in item.findall("category[@domain='post_tag']")
            if t.text
        ],
    }


def get_text(element: ET.Element, tag: str | None, ns: dict | None = None) -> str | None:
    if tag is None:
        return element.text.strip() if element.text else None
    if ns:
        for prefix, uri in ns.items():
            if tag.startswith(prefix + ":"):
                local = tag[len(prefix) + 1 :]
                for el in element.iter(f"{{{uri}}}{local}"):
                    return el.text.strip() if el.text else None
    for el in element.iter(tag):
        return el.text.strip() if el.text else None
    return None

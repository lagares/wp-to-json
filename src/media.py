import re
from pathlib import Path
from typing import Any


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}


def extract_media_urls(content: str) -> list[str]:
    if not content:
        return []

    url_pattern = r'https?://[^\s<>"\'\\]\S+(?:' + "|".join(re.escape(ext) for ext in IMAGE_EXTENSIONS) + r")"
    urls = re.findall(url_pattern, content, re.IGNORECASE)
    return list(set(urls))


def extract_media_from_posts(posts: list[dict]) -> dict[str, Any]:
    media_by_post = {}
    all_urls = set()

    for post in posts:
        urls = extract_media_urls(post.get("content", ""))
        if urls:
            media_by_post[post.get("slug") or post.get("id", "unknown")] = urls
            all_urls.update(urls)

    return {"by_post": media_by_post, "all": list(all_urls)}

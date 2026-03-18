import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from src.media import extract_media_from_posts, extract_media_urls
from src.parser import NS, get_text, parse_wordpress_xml


def validate_xml(xml_path: Path) -> tuple[bool, list[str]]:
    errors = []

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return False, [f"XML parse error: {e}"]

    channel = root.find("channel")
    if channel is None:
        errors.append("Missing required element: channel")
        return False, errors

    if get_text(channel, "title", NS) is None:
        errors.append("Missing required element: channel/title")

    posts = channel.findall("item")
    if not posts:
        errors.append("No items found in export")

    post_count = 0
    for item in posts:
        post_type = get_text(item, "wp:post_type", NS)
        if post_type == "post":
            post_count += 1

    if post_count == 0:
        errors.append("No posts found in export")

    for i, item in enumerate(posts[:5]):
        title = get_text(item, "title", NS)
        if not title:
            errors.append(f"Item {i+1}: Missing title")

    return len(errors) == 0, errors


def download_media(urls: list[str], output_dir: Path, dry_run: bool = False) -> dict:
    import urllib.request
    import urllib.error

    output_dir.mkdir(parents=True, exist_ok=True)
    results = {"downloaded": [], "failed": [], "dry_run": dry_run}

    for url in urls:
        filename = url.split("/")[-1].split("?")[0]
        if not filename:
            filename = f"image_{hash(url)}"

        filepath = output_dir / filename

        if dry_run:
            results["downloaded"].append({"url": url, "path": str(filepath)})
            continue

        try:
            urllib.request.urlretrieve(url, filepath)
            results["downloaded"].append({"url": url, "path": str(filepath)})
        except (urllib.error.URLError, OSError) as e:
            results["failed"].append({"url": url, "error": str(e)})

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Convert WordPress XML export to JSON"
    )
    parser.add_argument("input", help="WordPress XML export file")
    parser.add_argument("-o", "--output", help="Output JSON file (default: stdout)")
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty print JSON output"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate XML without exporting"
    )
    parser.add_argument(
        "--download-media",
        metavar="DIR",
        help="Download images from post content to specified directory",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        data = parse_wordpress_xml(input_path)
    except Exception as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run and not args.download_media:
        is_valid, errors = validate_xml(input_path)
        if is_valid:
            post_count = len(data.get("posts", []))
            print(f"Validation passed: {post_count} posts found, XML is valid")
            return
        else:
            print("Validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

    if args.download_media:
        media_info = extract_media_from_posts(data.get("posts", []))
        media_urls = media_info["all"]

        if not media_urls:
            print("No media URLs found in posts")
        else:
            output_dir = Path(args.download_media)
            print(f"Found {len(media_urls)} media URLs")

            if args.dry_run:
                results = download_media(media_urls, output_dir, dry_run=True)
            else:
                results = download_media(media_urls, output_dir)

            print(f"Would download {len(results['downloaded'])} files" if results["dry_run"] else f"Downloaded {len(results['downloaded'])} files")
            if results["failed"]:
                print(f"Failed: {len(results['failed'])}")

    json_output = json.dumps(data, indent=2 if args.pretty else None, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(json_output)
        print(f"Exported {len(data.get('posts', []))} posts to {args.output}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()

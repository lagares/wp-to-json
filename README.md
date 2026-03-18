# wp-to-json

Convert WordPress XML exports to JSON.

## Installation

```bash
pip install -e .
```

## Usage

```bash
wp-to-json <input.xml>                    # Output to stdout
wp-to-json <input.xml> -o output.json     # Output to file
wp-to-json <input.xml> --pretty -o out.json
```

## Features

### Dry-run Validation
Validate your WordPress XML export without generating output:

```bash
wp-to-json export.xml --dry-run
```

Checks for:
- Valid XML structure
- Required channel element
- Presence of posts
- Required fields on sample items

### Media Download
Extract and download images from post content:

```bash
wp-to-json export.xml --download-media ./images
wp-to-json export.xml --download-media ./images --dry-run  # Preview only
```

Supports: jpg, jpeg, png, gif, webp, svg, bmp

### Output Format

Each post includes:
- `title` - Post title
- `link` - Post URL
- `pub_date` - Publication date
- `content` - Full post content
- `excerpt` - Post excerpt
- `slug` - URL-friendly slug
- `status` - Publication status (publish, draft, etc.)
- `date` - WordPress post date
- `modified` - Last modified date
- `id` - WordPress post ID
- `categories` - List of categories
- `tags` - List of tags

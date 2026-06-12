"""Generate llms-full.txt and per-page .md files for LLM consumption."""

import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"
SITE_DIR = Path(__file__).parent.parent / "site"

# Ordered list of doc pages to include (relative to docs/)
PAGES = [
    "index.md",
    "tutorials/getting-started.md",
    "howto/deployment.md",
    "howto/configuration.md",
    "explanation/architecture.md",
    "reference/rest-api.md",
    "reference/for-coding-agents.md",
    "development/contributing.md",
]

# Regex to strip YAML frontmatter
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)

# Regex to strip snippet auto-append directives
SNIPPET_RE = re.compile(r"^\*\[.*?\]:.*$", re.MULTILINE)


def strip_frontmatter(content):
    """Remove YAML frontmatter from markdown content."""
    return FRONTMATTER_RE.sub("", content)


def strip_snippets(content):
    """Remove abbreviation snippet definitions appended by pymdownx.snippets."""
    return SNIPPET_RE.sub("", content)


def clean_content(content):
    """Strip frontmatter, snippets, and normalize whitespace."""
    content = strip_frontmatter(content)
    content = strip_snippets(content)
    return content.strip()


def main():
    """Generate llms-full.txt and individual .md files from doc sources."""
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    parts = []

    for page in PAGES:
        path = DOCS_DIR / page
        if not path.exists():
            print(f"Warning: {page} not found, skipping")
            continue
        content = clean_content(path.read_text(encoding="utf-8"))
        if not content:
            continue
        parts.append(content)

        # Write individual .md file to site directory
        md_path = SITE_DIR / page
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(content + "\n", encoding="utf-8")

    # Write concatenated llms-full.txt
    output = "\n\n---\n\n".join(parts) + "\n"
    out_path = SITE_DIR / "llms-full.txt"
    out_path.write_text(output, encoding="utf-8")
    print(f"Generated {out_path} ({len(parts)} pages, {len(output)} bytes)")
    print(f"Generated {len(parts)} individual .md files in {SITE_DIR}")


if __name__ == "__main__":
    main()

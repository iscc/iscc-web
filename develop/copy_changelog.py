"""Sync the repo-root CHANGELOG.md into the docs site as development/changelog.md."""

from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "CHANGELOG.md"
TARGET = ROOT / "docs" / "development" / "changelog.md"

FRONTMATTER = """\
---
# Generated from CHANGELOG.md by develop/copy_changelog.py - do not edit.
icon: lucide/history
description: Release history of the iscc-web microservice.
---

"""


def main():
    """Write docs/development/changelog.md from CHANGELOG.md if it is out of date."""
    content = FRONTMATTER + SOURCE.read_text(encoding="utf-8")
    if TARGET.exists() and TARGET.read_text(encoding="utf-8") == content:
        print(f"{TARGET.relative_to(ROOT)} is up to date")
        return
    TARGET.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

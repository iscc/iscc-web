"""
Maintain the version links in the repo-root CHANGELOG.md and sync it into the docs site as
development/changelog.md.

Every `## [X.Y.Z] - <date>` heading gets a link reference definition at the end of the file:
the oldest version links to its GitHub release, each later version to the compare view against
its predecessor, and an `Unreleased` version to the compare view against HEAD.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "CHANGELOG.md"
TARGET = ROOT / "docs" / "development" / "changelog.md"
REPO_URL = "https://github.com/iscc/iscc-web"
HEADING = re.compile(r"^## \[(\d+\.\d+\.\d+)\] - (.+)$", re.MULTILINE)
LINK = re.compile(r"^\[\d+\.\d+\.\d+\]: \S+\n?", re.MULTILINE)

FRONTMATTER = """\
---
# Generated from CHANGELOG.md by develop/copy_changelog.py - do not edit.
icon: lucide/history
description: Release history of the iscc-web microservice.
---

"""


def version_links(text):
    # type: (str) -> list[str]
    """Link reference definitions for all version headings in `text`, oldest version first."""
    links = []
    previous = None
    for version, date in reversed(HEADING.findall(text)):
        ref = "HEAD" if date.strip().lower() == "unreleased" else f"v{version}"
        url = f"{REPO_URL}/compare/{previous}...{ref}" if previous else f"{REPO_URL}/releases/tag/{ref}"
        links.append(f"[{version}]: {url}")
        previous = f"v{version}"
    return links


def with_version_links(text):
    # type: (str) -> str
    """Return `text` with its version link definitions replaced by freshly generated ones."""
    body = LINK.sub("", text).rstrip("\n")
    return body + "\n\n" + "\n".join(version_links(text)) + "\n"


def write_if_changed(path, content):
    # type: (Path, str) -> None
    """Write `content` to `path` unless the file already holds exactly that content."""
    if path.exists() and path.read_text(encoding="utf-8") == content:
        print(f"{path.relative_to(ROOT)} is up to date")
        return
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {path.relative_to(ROOT)}")


def main():
    """Refresh the version links in CHANGELOG.md, then write docs/development/changelog.md from it."""
    changelog = with_version_links(SOURCE.read_text(encoding="utf-8"))
    write_if_changed(SOURCE, changelog)
    write_if_changed(TARGET, FRONTMATTER + changelog)


if __name__ == "__main__":
    main()

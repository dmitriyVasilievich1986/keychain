#!/usr/bin/env python3
"""Calculate the next application version for a merged pull request.

Rules:
    * The latest stable git tag (``X.Y.Z``) is the base version; ``0.0.0`` if none.
    * A PR merged into ``development`` bumps the patch version.
    * If a PR commit subject starts with ``version(application):``, the version
      written after it is used as-is and auto-increment is skipped. When several
      commits match, the most recent one wins.

The result is printed and, when running in GitHub Actions, written to
``$GITHUB_OUTPUT`` as ``version=<value>``.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

OVERRIDE_RE = re.compile(r"^version\(application\):\s*(\S+)")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")
STABLE_TAG_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
COMMIT_SEPARATOR = "\x1e"  # ASCII record separator between commit messages

type SemVer = tuple[int, int, int]


class VersionError(Exception):
    """Raised when a version cannot be calculated."""


def find_override(messages: list[str]) -> str | None:
    """Return the version from the most recent ``version(application):`` commit.

    Only the first line (subject) of each commit message is checked.
    ``messages`` must be ordered oldest first, as the GitHub API returns them.
    """
    override = None
    for message in messages:
        subject = message.strip().splitlines()[0] if message.strip() else ""
        if match := OVERRIDE_RE.match(subject):
            override = match.group(1)

    if override is not None and not VERSION_RE.match(override):
        raise VersionError(
            f"Invalid version in 'version(application):' commit: {override!r}. "
            "Expected X.Y.Z or X.Y.Z-suffix (e.g. 2.0.0, 1.2.3-dev)."
        )
    return override


def latest_stable_tag(tags: list[str]) -> SemVer:
    """Return the highest ``X.Y.Z`` tag, ignoring pre-release tags; ``0.0.0`` if none."""
    versions = [
        (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        for tag in tags
        if (m := STABLE_TAG_RE.match(tag.strip()))
    ]
    return max(versions, default=(0, 0, 0))


def bump(base: SemVer) -> str:
    """Bump the patch version of ``base``."""
    major, minor, patch = base
    return f"{major}.{minor}.{patch + 1}"


def calculate(messages: list[str], tags: list[str]) -> str:
    """Return the new version, rejecting one that already exists as a tag."""
    version = find_override(messages) or bump(latest_stable_tag(tags))
    if version in {tag.strip() for tag in tags}:
        raise VersionError(f"Tag {version!r} already exists")
    return version


def _git_tags() -> list[str]:
    result = subprocess.run(
        ["git", "tag", "--list"], check=True, capture_output=True, text=True
    )
    return result.stdout.splitlines()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--commits",
        type=Path,
        required=True,
        help=f"File with PR commit messages separated by {COMMIT_SEPARATOR!r}",
    )
    args = parser.parse_args()

    messages = [
        m for m in args.commits.read_text().split(COMMIT_SEPARATOR) if m.strip()
    ]

    try:
        version = calculate(messages, _git_tags())
    except VersionError as e:
        print(f"::error::{e}", file=sys.stderr)
        sys.exit(1)

    print(f"Calculated version: {version}")
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a") as f:
            f.write(f"version={version}\n")


if __name__ == "__main__":
    main()

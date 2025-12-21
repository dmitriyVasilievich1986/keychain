#!/usr/bin/env python3
"""Version bumping script for keychain project.

Handles version bumping for both Python (__init__.py) and JSON (package.json) files.
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


def parse_version(version_string: str) -> Tuple[int, int, int]:
    """Parse semantic version string into major, minor, patch components.

    Args:
        version_string: Version string in format "X.Y.Z"

    Returns:
        Tuple of (major, minor, patch) as integers

    """
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_string)
    if not match:
        raise ValueError(f"Invalid version format: {version_string}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version components into semantic version string."""
    return f"{major}.{minor}.{patch}"


def bump_version(version_string: str, branch: str) -> str:
    """Bump version based on branch name.

    Args:
        version_string: Current version string
        branch: Git branch name (development or master)

    Returns:
        New bumped version string

    """
    major, minor, patch = parse_version(version_string)

    if branch == "development":
        # Bump PATCH version for development branch
        patch += 1
    elif branch == "master":
        # Bump MINOR version for master branch
        minor += 1
        patch = 0  # Reset patch when bumping minor
    else:
        raise ValueError(f"Unsupported branch: {branch}")

    return format_version(major, minor, patch)


def get_python_version(file_path: Path) -> str:
    """Extract version from Python __init__.py file.

    Expected format: __version__ = "X.Y.Z"
    """
    content = file_path.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError(f"Could not find __version__ in {file_path}")
    return match.group(1)


def set_python_version(file_path: Path, new_version: str) -> None:
    """Update version in Python __init__.py file."""
    content = file_path.read_text()
    new_content = re.sub(r'(__version__\s*=\s*["\'])[^"\']+(["\'])', rf"\g<1>{new_version}\g<2>", content)
    file_path.write_text(new_content)


def get_json_version(file_path: Path) -> str:
    """Extract version from JSON file (package.json)."""
    data = json.loads(file_path.read_text())
    if "version" not in data:
        raise ValueError(f"Could not find version field in {file_path}")
    return data["version"]


def set_json_version(file_path: Path, new_version: str) -> None:
    """Update version in JSON file (package.json)."""
    data = json.loads(file_path.read_text())
    data["version"] = new_version
    file_path.write_text(json.dumps(data, indent=2) + "\n")


def main():
    """Main entry point for version bumping script."""
    parser = argparse.ArgumentParser(description="Bump version in project files")
    parser.add_argument("--file", required=True, type=Path, help="Path to file to update")
    parser.add_argument("--type", required=True, choices=["python", "json"], help="Type of file to update")
    parser.add_argument("--branch", help="Branch name (development or master)")
    parser.add_argument("--get-version", action="store_true", help="Only get current version without bumping")

    args = parser.parse_args()

    # Get current version based on file type
    if args.type == "python":
        current_version = get_python_version(args.file)
    elif args.type == "json":
        current_version = get_json_version(args.file)
    else:
        logger.error(f"Unsupported file type: {args.type}")
        sys.exit(1)

    # If only getting version, print and exit
    if args.get_version:
        logger.info(current_version)
        return

    # Validate branch argument is provided for bumping
    if not args.branch:
        logger.error("--branch is required when not using --get-version")
        sys.exit(1)

    # Bump version
    try:
        new_version = bump_version(current_version, args.branch)
    except ValueError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

    # Update file with new version
    if args.type == "python":
        set_python_version(args.file, new_version)
    elif args.type == "json":
        set_json_version(args.file, new_version)

    logger.info(f"Version bumped: {current_version} -> {new_version}")
    logger.info(f"File updated: {args.file}")


if __name__ == "__main__":
    main()

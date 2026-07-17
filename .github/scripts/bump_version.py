#!/usr/bin/env python3
"""Version bumping script for Expenses Counter project.

Handles version bumping for both Python (src/keychain/__init__.py) and JSON (package.json) files.
"""

# region Import libraries

import argparse
import json
import logging
import re
import sys
from abc import ABC, abstractmethod
from argparse import Namespace
from enum import StrEnum
from pathlib import Path
from typing import Any, cast, Dict, List, Tuple

# endregion Import libraries

# region Logging

logger = logging.getLogger("BumpVersion")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

# endregion Logging

# region Constants

BASE_FOLDER_PATH = Path(__file__).parent.parent.parent
PYTHON_FILE_PATH = BASE_FOLDER_PATH / "backend" / "src" / "keychain" / "__init__.py"
PACKAGE_JSON_FILE_PATH = BASE_FOLDER_PATH / "frontend" / "package.json"
PACKAGE_LOCK_JSON_FILE_PATH = BASE_FOLDER_PATH / "frontend" / "package-lock.json"
APPLICATION_VERSION_FILE = BASE_FOLDER_PATH / "frontend" / "src" / "utils" / "application-version.json"

# endregion Constants

# region Enums


class VersionType(StrEnum):
    patch = "PATCH"
    minor = "MINOR"
    major = "MAJOR"


class FileType(StrEnum):
    """Supported project file kinds for version read/write."""

    backend = "backend"
    frontend = "frontend"
    application = "application"
    all = "all"


class Arguments:
    """Class for CLI arguments."""

    type: FileType
    version_type: VersionType
    get_version: bool


# endregion Enums

# region Main classes


class Version:
    """Semantic version (major.minor.patch) with bump helpers."""

    major: int
    minor: int
    patch: int

    def __init__(self, line: str) -> None:
        """Parse a dotted version string into major, minor, and patch.

        Args:
            line (str): Version string in ``major.minor.patch`` form.

        Raises:
            ValueError: If ``line`` does not match the expected format.

        """
        self.major, self.minor, self.patch = self._parse_version(str(line))
        self.current_version = str(self)

    def __str__(self) -> str:
        """Format the version as ``major.minor.patch``.

        Returns:
            str: Dotted version string.

        """
        return f"{self.major}.{self.minor}.{self.patch}"

    def _parse_version(self, line: str) -> Tuple[int, int, int]:
        """Extract major, minor, and patch integers from a version string.

        Args:
            line (str): Version string to parse.

        Returns:
            Tuple[int, int, int]: Parsed ``(major, minor, patch)`` tuple.

        Raises:
            ValueError: If ``line`` is not three dot-separated integers.

        """
        matched_version = re.match(r"^(\d+)\.(\d+)\.(\d+)$", line)
        if not matched_version:
            logger.error(f"Invalid version format: {line}")
            raise ValueError(f"Invalid version format: {line}")

        payload = int(matched_version.group(1)), int(matched_version.group(2)), int(matched_version.group(3))
        logger.info(f"Parsed version: {payload}")
        return payload

    def bump_patch(self) -> None:
        """Increment the patch component by one.

        Returns:
            None

        """
        self.patch += 1

    def bump_minor(self) -> None:
        """Increment the minor component and reset patch to zero.

        Returns:
            None

        """
        self.minor += 1
        self.patch = 0

    def bump_major(self) -> None:
        """Increment the major component and reset minor and patch to zero.

        Returns:
            None

        """
        self.major += 1
        self.minor = 0
        self.patch = 0


class FileHandler(ABC):
    """Abstract handler for reading, bumping, and persisting a project version file."""

    extension: str
    name: str

    def __init__(self, file_path: Path) -> None:
        """Load the current version from the target file.

        Args:
            file_path (Path): Path to the version-bearing file.

        Raises:
            FileNotFoundError: If ``file_path`` does not exist.
            ValueError: If the file suffix does not match the handler extension.

        """
        self.file_path = file_path
        if not self.file_path.exists():
            logger.error(f"File {self.file_path} does not exist")
            raise FileNotFoundError(f"File {self.file_path} does not exist")

        if self.file_path.suffix != self.extension:
            logger.error(f"File {self.file_path} is not a {self.extension} file")
            raise ValueError(f"File {self.file_path} is not a {self.extension} file")

        logger.info(f"Getting {self.name} version from {self.file_path}")
        self.version = Version(self._get_version())

    @abstractmethod
    def _read_file(self) -> Any:
        """Read and return the raw file contents in the handler-specific format.

        Returns:
            Any: Parsed or raw file data.

        """
        pass

    @abstractmethod
    def _write_file(self, data: Any) -> None:
        """Persist handler-specific data to ``self.file_path``.

        Args:
            data (Any): Data produced by ``_read_file`` with an updated version.

        Returns:
            None

        """
        pass

    @abstractmethod
    def _get_version(self) -> str:
        """Extract the current version string from the file.

        Returns:
            str: Current semantic version.

        Raises:
            ValueError: If the version cannot be found in the file.

        """
        pass

    @abstractmethod
    def save(self) -> None:
        """Write the bumped version back to ``self.file_path``.

        Returns:
            None

        """
        pass

    def bump_version(self, version_type: VersionType) -> None:
        """Apply branch-specific bump rules to ``self.version``.

        On ``VersionType.patch``, bumps patch; on ``VersionType.minor``,
        bumps minor and resets patch; on ``VersionType.major``,
        bumps major and resets minor and patch.

        Args:
            version_type (VersionType): Version type to bump.

        Returns:
            None

        Raises:
            ValueError: If ``version_type`` is not a supported value.

        """
        if version_type == VersionType.patch:
            self.version.bump_patch()
        elif version_type == VersionType.minor:
            self.version.bump_minor()
        elif version_type == VersionType.major:
            self.version.bump_major()
        else:
            logger.error(f"Invalid version type: {version_type}")
            raise ValueError(f"Invalid version type: {version_type}")
        logger.info(f"Bumped version: {self.version.current_version} -> {self.version}")
        logger.info(f"{self.name} version set: {self.file_path} -> {self.version}")


class JSONFileHandler(FileHandler):
    """Read and update a ``version`` field in a JSON file."""

    extension = ".json"
    name = "JSON"

    def _read_file(self) -> Dict[str, Any]:
        """Load JSON object from ``self.file_path``.

        Returns:
            Dict[str, Any]: Parsed JSON root object.

        """
        with self.file_path.open("r") as f:
            return json.load(f)

    def _write_file(self, data: Dict[str, Any]) -> None:
        """Serialize and write a JSON object to ``self.file_path``.

        Args:
            data (Dict[str, Any]): JSON root object to persist.

        Returns:
            None

        """
        with self.file_path.open("w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

    def _get_version(self) -> str:
        """Return the ``version`` key from the JSON root object.

        Returns:
            str: Current version string.

        Raises:
            ValueError: If the JSON object has no ``version`` field.

        """
        data = self._read_file()
        if not (version := data.get("version")):
            logger.error(f"Could not find version field in {self.file_path}")
            raise ValueError(f"Could not find version field in {self.file_path}")

        return version

    def save(self) -> None:
        """Update the ``version`` key and write the JSON file.

        Returns:
            None

        """
        data = self._read_file()
        data["version"] = str(self.version)
        self._write_file(data)
        logger.info(f"File updated: {self.file_path}")


class PythonFileHandler(FileHandler):
    """Read and update ``__version__`` in a Python module file."""

    extension = ".py"
    name = "Python"

    def _read_file(self) -> str:
        """Read the full text of ``self.file_path``.

        Returns:
            str: File contents.

        """
        with self.file_path.open("r") as f:
            return f.read()

    def _write_file(self, data: str) -> None:
        """Overwrite ``self.file_path`` with the given text.

        Args:
            data (str): Full file contents to write.

        Returns:
            None

        """
        with self.file_path.open("w") as f:
            f.write(data)

    def _get_version(self) -> str:
        """Extract ``__version__`` from the module source.

        Returns:
            str: Quoted version string assigned to ``__version__``.

        Raises:
            ValueError: If no ``__version__`` assignment is found.

        """
        content = self._read_file()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if not match:
            logger.error(f"Could not find __version__ in {self.file_path}")
            raise ValueError(f"Could not find __version__ in {self.file_path}")

        return match.group(1)

    def save(self) -> None:
        """Replace ``__version__`` in the module and write the file.

        Returns:
            None

        """
        content = self._read_file()
        content = re.sub(r'(__version__\s*=\s*["\'])[^"\']+(["\'])', rf"\g<1>{self.version}\g<2>", content)
        self._write_file(content)
        logger.info(f"File updated: {self.file_path}")


# endregion Main classes

# region Main functions


def _get_namespace() -> Namespace:
    """Parse CLI arguments for version get or bump operations.

    Returns:
        Namespace: Parsed arguments with ``type``, ``version-type``, and
            ``get_version`` attributes.

    """
    parser = argparse.ArgumentParser(description="Bump version in project files")
    parser.add_argument("--type", required=True, choices=FileType, help="Type of file to update")
    parser.add_argument("--version-type", required=False, choices=VersionType, help="Version type to bump")
    parser.add_argument("--get-version", action="store_true", help="Only get current version without bumping")
    return parser.parse_args()


def main():
    """Run version read or bump for the requested file type and branch.

    Exits with status 1 on unsupported file type, missing ``--branch`` when
    bumping, or bump validation errors.

    Returns:
        None

    """
    args = cast(Arguments, _get_namespace())
    file_type_handlers: Dict[FileType, List[FileHandler]] = {
        FileType.backend: [PythonFileHandler(PYTHON_FILE_PATH)],
        FileType.frontend: [JSONFileHandler(PACKAGE_JSON_FILE_PATH), JSONFileHandler(PACKAGE_LOCK_JSON_FILE_PATH)],
        FileType.application: [JSONFileHandler(APPLICATION_VERSION_FILE)],
        FileType.all: [
            PythonFileHandler(PYTHON_FILE_PATH),
            JSONFileHandler(PACKAGE_JSON_FILE_PATH),
            JSONFileHandler(PACKAGE_LOCK_JSON_FILE_PATH),
            JSONFileHandler(APPLICATION_VERSION_FILE),
        ],
    }

    # Get current version based on file type
    if args.type not in file_type_handlers:
        logger.error(f"Unsupported file type: {args.type}")
        sys.exit(1)

    handlers = file_type_handlers[args.type]

    # If only getting version, print and exit
    if args.get_version:
        for handler in handlers:
            logger.info(f"{handler.name}. Path: {handler.file_path}. Version: {handler.version}")
        return

    # Validate branch argument is provided for bumping
    if not args.version_type:
        logger.error("--version-type is required when not using --get-version")
        sys.exit(1)

    # Bump version
    try:
        for handler in handlers:
            handler.bump_version(args.version_type)
    except ValueError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

    # Update file with new version
    for handler in handlers:
        handler.save()


if __name__ == "__main__":
    main()

# endregion Main functions

"""Utility functions for documentation generation."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Optional

import pypandoc
from loguru import logger

def find_project_root() -> Path:
    """Find the project root directory by looking for pyproject.toml.

    Returns:
        Path: Project root directory path

    Raises:
        FileNotFoundError: If project root cannot be determined
    """
    current = Path(__file__).resolve().parent

    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent

    raise FileNotFoundError(
        "Could not determine project root. No pyproject.toml found in parent directories."
    )

# Constants
PROJECT_ROOT: Final[Path] = find_project_root()
DOCS_DIR: Final[Path] = PROJECT_ROOT / "docs"
README_PATH: Final[Path] = PROJECT_ROOT / "README.md"

BADGES: Final[str] = """
[![Ruff Code Quality Badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://docs.astral.sh/ruff/)
[![Documentation Built by Sphinx](https://img.shields.io/badge/Documentation-Built%20with%20Sphinx-blue?logo=read-the-docs&logoColor=white)](https://www.sphinx-doc.org)
[![Project Built with Hatchling](https://img.shields.io/badge/Project-Built%20with%20Hatchling-green?logo=python)](https://hatch.pypa.io/latest/)
"""

@dataclass
class RstFile:
    """Represents an RST documentation file with metadata."""

    path: Path
    title: str
    section_level: int = 2
    last_modified: float = field(init=False)

    def __post_init__(self) -> None:
        """Initialize last_modified timestamp."""
        self.last_modified = self._get_last_modified()

    def _get_last_modified(self) -> float:
        """Get the last modified timestamp of the file.

        Returns:
            float: Last modified timestamp
        """
        try:
            return os.path.getmtime(self.path)
        except OSError:
            return 0.0

    def needs_update(self, readme_mtime: float) -> bool:
        """Check if this file has been modified since last README generation.

        Args:
            readme_mtime: Timestamp of current README.md

        Returns:
            bool: True if file is newer than README
        """
        if not self.path.exists():
            return False
        return self._get_last_modified() > readme_mtime

    def convert_to_md(self) -> Optional[str]:
        """Convert RST content to markdown using pypandoc.

        Returns:
            Optional[str]: Converted markdown content
        """
        try:
            if not self.path.exists():
                logger.warning(f"RST file not found: {self.path}")
                return None

            content = self.path.read_text()
            # Convert RST to markdown using pypandoc
            md_content = pypandoc.convert_text(
                content,
                "gfm",  # GitHub-Flavored Markdown
                format="rst",
                extra_args=["--wrap=preserve", "--columns=100"]
            )
            # Clean up the content
            md_content = self._clean_content(md_content)
            # Add section header
            header = f"{'#' * self.section_level} {self.title}\n\n"
            return header + md_content

        except Exception as e:
            logger.error(f"Failed to convert {self.path}: {e}")
            return None

    def _clean_content(self, content: str) -> str:
        """Clean up converted markdown content.

        Args:
            content: Raw converted markdown

        Returns:
            str: Cleaned markdown content
        """
        # Remove title from content since we add our own
        lines = content.split("\n")
        while lines and (not lines[0].strip() or lines[0].startswith("#")):
            lines.pop(0)

        # Join lines and clean up excessive newlines
        return "\n".join(lines).strip()


def check_needs_update() -> bool:
    """Check if README.md needs to be regenerated.

    Returns:
        bool: True if README needs update
    """
    if not README_PATH.exists():
        return True

    readme_mtime = os.path.getmtime(README_PATH)
    source_files = [
        RstFile(DOCS_DIR / "user" / "quickstart.rst", "Quick Start"),
        RstFile(DOCS_DIR / "dev" / "contributing.rst", "Contributing"),
    ]

    return any(f.needs_update(readme_mtime) for f in source_files)

def generate_readme(force: bool = False) -> None:
    """Generate README.md file from RST documentation.

    Args:
        force: Force README generation even if files unchanged
    """
    if not force and not check_needs_update():
        logger.info("README.md is up to date")
        return

    source_files = [
        RstFile(DOCS_DIR / "user" / "quickstart.rst", "Quick Start"),
        RstFile(DOCS_DIR / "dev" / "contributing.rst", "Contributing"),
    ]

    try:
        logger.info("Generating README.md...")

        # Start with header and badges
        content = [
            "# Http Dynamix",
            BADGES,
            "Library for creating dynamic HTTP requests in puthon",
            "",
        ]

        # Convert and add each RST file
        for rst_file in source_files:
            converted = rst_file.convert_to_md()
            if converted:
                content.extend([converted, ""])

        # Write the README file
        README_PATH.write_text("\n".join(content))
        logger.info(f"Successfully generated {README_PATH} at {README_PATH.absolute()}")

    except Exception as e:
        logger.error(f"Failed to generate README.md: {e}")
        raise

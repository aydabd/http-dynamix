"""HTTPX Logger with Pluggable Formatters."""

from __future__ import annotations

import base64
import csv
import json
import xml.dom.minidom
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum, auto
from io import StringIO
from typing import Any, Protocol, runtime_checkable

import httpx
import yaml
from bs4 import BeautifulSoup

from http_dynamix.log import log as logger


class ContentCategory(StrEnum):
    """Enumeration for content categories."""

    TEXT = auto()
    BINARY = auto()
    STRUCTURED = auto()
    FORM = auto()
    UNKNOWN = auto()


@runtime_checkable
class ContentFormatter(Protocol):
    """Protocol for content formatters."""

    @property
    @abstractmethod
    def content_types(self) -> set[str]:
        """Set of content types this formatter can handle."""
        ...

    @property
    @abstractmethod
    def category(self) -> ContentCategory:
        """Category of content this formatter handles."""
        ...

    @abstractmethod
    def can_handle(self, content_type: str) -> bool:
        """Check if this formatter can handle the given content type."""
        ...

    @abstractmethod
    def format(self, content: str | bytes, max_length: int | None = None) -> str:
        """Format the content."""
        ...


@dataclass
class JsonFormatter:
    """Formatter for JSON content."""

    content_types: set[str] = field(default_factory=lambda: {"application/json"})
    category: ContentCategory = ContentCategory.STRUCTURED

    def can_handle(self, content_type: str) -> bool:
        """Check if this formatter can handle the given content type.

        Args:
            content_type: Content type to check.

        Returns:
            bool: True if this formatter can handle the content type.
        """
        return any(ct in content_type.lower() for ct in self.content_types)

    def format(self, content: str | bytes, max_length: int | None = None) -> str:
        """Format the JSON content.

        Args:
            content: JSON content to format.
            max_length: Maximum length of formatted content.

        Returns:
            Formatted JSON content.
        """
        try:
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=2)
            if max_length and len(formatted) > max_length:
                return f"{formatted[:max_length]}... [truncated]"
            return formatted
        except Exception as e:
            return f"[Error formatting JSON: {str(e)}]"


@dataclass
class XmlFormatter:
    """Formatter for XML content."""

    content_types: set[str] = field(
        default_factory=lambda: {"application/xml", "text/xml"}
    )
    category: ContentCategory = ContentCategory.STRUCTURED

    def can_handle(self, content_type: str) -> bool:
        """Check if this formatter can handle the given content type.

        Args:
            content_type: Content type to check.

        Returns:
            bool: True if this formatter can handle the content type.
        """
        return any(ct in content_type.lower() for ct in self.content_types)

    def format(self, content: str | bytes, max_length: int | None = None) -> str:
        """Format the XML content.

        Args:
            content: XML content to format.
            max_length: Maximum length of formatted content.

        Returns:
            Formatted XML content.
        """
        try:
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            parsed = xml.dom.minidom.parseString(content)
            formatted = parsed.toprettyxml(indent="  ")
            if max_length and len(formatted) > max_length:
                return f"{formatted[:max_length]}... [truncated]"
            return formatted
        except Exception as e:
            return f"[Error formatting XML: {str(e)}]"


@dataclass
class HtmlFormatter:
    """Formatter for HTML content.

    This formatter uses BeautifulSoup to prettify the HTML content.

    Args:
        content_types: Set of content types this formatter can handle.
        category: Category of content this formatter handles.
    """

    content_types: set[str] = field(default_factory=lambda: {"text/html"})
    category: ContentCategory = ContentCategory.STRUCTURED

    def can_handle(self, content_type: str) -> bool:
        """Check if this formatter can handle the given content type.

        Args:
            content_type: Content type to check.

        Returns:
            bool: True if this formatter can handle the content type.
        """
        return any(ct in content_type.lower() for ct in self.content_types)

    def format(self, content: str | bytes, max_length: int | None = None) -> Any:
        """Format the HTML content.

        Args:
            content: HTML content to format.
            max_length: Maximum length of formatted content.

        Returns:
            Formatted HTML content.
        """
        try:
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            soup = BeautifulSoup(content, "html.parser")
            formatted = soup.prettify()
            if max_length and len(formatted) > max_length:
                return f"{str(formatted)[:max_length]}... [truncated]"
            return formatted
        except Exception as e:
            return f"[Error formatting HTML: {str(e)}]"


@dataclass
class CsvFormatter:
    """Formatter for CSV content.

    This formatter formats CSV content in a tabular format.

    Args:
        content_types: Set of content types this formatter can handle.
        category: Category of content this formatter handles.
    """

    content_types: set[str] = field(default_factory=lambda: {"text/csv"})
    category: ContentCategory = ContentCategory.STRUCTURED

    def can_handle(self, content_type: str) -> bool:
        """Check if this formatter can handle the given content type.

        Args:
            content_type: Content type to check.

        Returns:
            bool: True if this formatter can handle the content type.
        """
        return any(ct in content_type.lower() for ct in self.content_types)

    def format(self, content: str | bytes, max_length: int | None = None) -> str:
        """Format the CSV content.

        Args:
            content: CSV content to format.
            max_length: Maximum length of formatted content.

        Returns:
            Formatted CSV content.
        """
        try:
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            csv_reader = csv.reader(StringIO(content))
            rows = list(csv_reader)
            if not rows:
                return "[Empty CSV]"

            col_widths = [
                max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))
            ]
            formatted_rows = []

            for row in rows:
                formatted_row = " | ".join(
                    str(cell).ljust(width) for cell, width in zip(row, col_widths)
                )
                formatted_rows.append(f"| {formatted_row} |")

            separator = "-" * len(formatted_rows[0])
            formatted_rows.insert(1, separator)

            formatted = "\n".join(formatted_rows)
            if max_length and len(formatted) > max_length:
                return f"{formatted[:max_length]}... [truncated]"
            return formatted
        except Exception as e:
            return f"[Error formatting CSV: {str(e)}]"


@dataclass
class BinaryFormatter:
    """Formatter for binary content.

    This formatter formats binary content as a JSON object with size and
    optionally content.

    Args:
        content_types: Set of content types this formatter can handle.
        category: Category of content this formatter handles.
        include_content: Include content in the formatted output.
        max_file_size: Maximum file size to include content (in bytes).
    """

    content_types: set[str] = field(
        default_factory=lambda: {"application/octet-stream"}
    )
    category: ContentCategory = ContentCategory.BINARY
    include_content: bool = False
    max_file_size: int = 1024 * 1024  # 1MB

    def can_handle(self, content_type: str) -> bool:
        """Check if this formatter can handle the given content type.

        Args:
            content_type: Content type to check.

        Returns:
            bool: True if this formatter can handle the content type.
        """
        return True  # Can handle any binary content as fallback

    def format(self, content: str | bytes, max_length: int | None = None) -> str:
        """Format the binary content.

        Args:
            content: Binary content to format.
            max_length: Maximum length of formatted content.

        Returns:
            Formatted binary content.
        """
        try:
            if isinstance(content, str):
                content = content.encode("utf-8")
            content_length = len(content)
            file_info = {"size": f"{content_length / 1024:.2f}KB", "binary": True}
            if (
                self.include_content and content_length <= self.max_file_size
            ):  # pragma: no cover # noqa: E501
                file_info["content"] = base64.b64encode(content).decode("utf-8")
            return json.dumps(file_info, indent=2)
        except Exception as e:
            return f"[Error formatting binary content: {str(e)}]"


@dataclass
class FormDataFormatter:
    """Formatter for multipart form data.

    This formatter formats multipart form data as a list of parts with
    headers and content.

    Args:
        content_types: Set of content types this formatter can handle.
        category: Category of content this formatter handles.
    """

    content_types: set[str] = field(default_factory=lambda: {"multipart/form-data"})
    category: ContentCategory = ContentCategory.FORM

    def can_handle(self, content_type: str) -> bool:
        """Check if this formatter can handle the given content type.

        Args:
            content_type: Content type to check.

        Returns:
            bool: True if this formatter can handle the content type.
        """
        return any(ct in content_type.lower() for ct in self.content_types)

    def format(self, content: str | bytes, max_length: int | None = None) -> str:
        """Format the multipart form data.

        Args:
            content: Multipart form data content to format.
            max_length: Maximum length of formatted content.

        Returns:
            Formatted multipart form data.
        """
        try:
            if isinstance(content, str):
                content = content.encode("utf-8")  # pragma: no cover

            # Extract boundary from content type
            boundary = None
            if isinstance(content, bytes) and b"boundary=" in content:
                boundary = content.split(b"boundary=")[1].split(b"\r\n")[0]

            if not boundary:
                return "[Error: No boundary found in multipart form data]"

            parts = content.split(boundary)
            formatted_parts = []

            for part in parts[1:-1]:
                if part:  # pragma: no cover
                    # Strip leading/trailing whitespace and split headers and content
                    part = part.strip(b"\r\n--")
                    headers, _, content = part.partition(b"\r\n\r\n")
                    formatted_parts.append(
                        {
                            "headers": headers.decode("utf-8", errors="replace"),
                            "content": "[Binary content]"
                            if b"\x00" in content
                            else content.decode("utf-8", errors="replace"),
                        }
                    )

            formatted = json.dumps(formatted_parts, indent=2)
            if max_length and len(formatted) > max_length:
                return f"{formatted[:max_length]}... [truncated]"  # pragma: no cover
            return formatted
        except Exception as e:  # pragma: no cover
            return f"[Error formatting form data: {str(e)}]"


@dataclass
class HttpResponseLogger:
    """Logger for HTTP responses with pluggable formatters.

    Args:
        debug_mode: Enable or disable debug mode.
        max_body_length: Maximum length of response body to log.
        sensitive_headers: Set of sensitive headers to mask.
        formatters: List of content formatters to use.

    Examples:
        .. code-block:: python

            logger = HttpResponseLogger()
            logger.log_response(response)
    """

    debug_mode: bool = True
    max_body_length: int = 1000
    sensitive_headers: set[str] = field(
        default_factory=lambda: {
            "authorization",
            "cookie",
            "set-cookie",
            "x-api-key",
            "api-key",
            "access-token",
            "refresh-token",
        }
    )
    formatters: list[ContentFormatter] = field(
        default_factory=lambda: [
            JsonFormatter(),
            XmlFormatter(),
            HtmlFormatter(),
            CsvFormatter(),
            FormDataFormatter(),
            YamlFormatter(),
            TextFormatter(),  # Add TextFormatter before BinaryFormatter
            BinaryFormatter(include_content=True),
        ]
    )

    def __sanitize_sensitive_parts(self, message: str, hidden_parts: set[str]) -> str:
        """Sanitize sensitive parts of the message.

        Args:
            message: Message to sanitize.
            hidden_parts: Set of sensitive parts to hide.

        Returns:
            Sanitized message.
        """
        if not hidden_parts:
            return message  # pragma: no cover

        for part in hidden_parts:
            message = message.replace(part, "**********")
        return message

    def _format_headers(self, headers: httpx.Headers) -> dict[str, str]:
        """Format headers, masking sensitive information.

        Args:
            headers: Headers to format.

        Returns:
            Formatted headers.
        """
        return {
            key: self.__sanitize_sensitive_parts(value, self.sensitive_headers)
            for key, value in headers.items()
        }

    def _get_formatter(self, content_type: str) -> ContentFormatter | None:
        for formatter in self.formatters:
            if formatter.can_handle(content_type):
                return formatter
        return None  # pragma: no cover

    def _format_content(self, response: httpx.Response) -> str | None:
        """Format response content based on content type."""
        status_code = getattr(response, "status_code", None)
        if status_code == 204 or not response.content:
            return None

        content_type = response.headers.get("content-type", "").lower()
        formatter = self._get_formatter(content_type)

        if formatter:
            return formatter.format(response.content, self.max_body_length)
        return f"[No formatter available for content-type: {content_type}]"  # pragma: no cover # noqa: E501

    def log_response(self, response: httpx.Response) -> None:
        """Log HTTP response with appropriate formatting.

        Args:
            response: HTTP response to log.
        """
        if not self.debug_mode:
            return

        try:
            status_code = response.status_code
        except Exception:
            status_code = -1
        try:
            elapsed = f"{response.elapsed.total_seconds():.3f}s"
        except Exception:
            elapsed = "n/a"
        log_data = {
            "url": str(response.url),
            "status_code": status_code,
            "headers": self._format_headers(response.headers),
            "elapsed": elapsed,
        }

        formatted_content = self._format_content(response)
        if formatted_content:
            log_data["body"] = formatted_content

        logger.debug(f"HTTP Response: {log_data!r}")  # pragma: no cover


# Example of adding a custom formatter:
@dataclass
class YamlFormatter:
    """Custom formatter for YAML content.

    This formatter formats YAML content using the PyYAML library.

    Args:
        content_types: Set of content types this formatter can handle.
        category: Category of content this formatter handles.
    """

    content_types: set[str] = field(
        default_factory=lambda: {"application/yaml", "text/yaml"}
    )
    category: ContentCategory = ContentCategory.STRUCTURED

    def can_handle(self, content_type: str) -> bool:
        """Check if this formatter can handle the given content type.

        Args:
            content_type: Content type to check.

        Returns:
            bool: True if this formatter can handle the content type.
        """
        return any(ct in content_type.lower() for ct in self.content_types)

    def format(self, content: str | bytes, max_length: int | None = None) -> str:
        """Format the YAML content.

        Args:
            content: YAML content to format.
            max_length: Maximum length of formatted content.

        Returns:
            Formatted YAML content.
        """
        try:
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            parsed = yaml.safe_load(content)
            formatted = yaml.dump(parsed, indent=2, allow_unicode=True)
            if max_length and len(formatted) > max_length:
                return f"{formatted[:max_length]}... [truncated]"
            return formatted
        except Exception as e:
            return f"[Error formatting YAML: {str(e)}]"


@dataclass
class TextFormatter:
    """Formatter for plain text content."""

    content_types: set[str] = field(default_factory=lambda: {"text/plain"})
    category: ContentCategory = ContentCategory.TEXT

    def can_handle(self, content_type: str) -> bool:
        """Check if this formatter can handle the given content type.

        Args:
            content_type: Content type to check.

        Returns:
            bool: True if this formatter can handle the content type.
        """
        content_type = content_type.strip().lower()
        return any(ct == content_type for ct in self.content_types)

    def format(self, content: str | bytes, max_length: int | None = None) -> str:
        """Format the text content.

        Args:
            content: Text content to format.
            max_length: Maximum length of formatted content.

        Returns:
            str: Formatted text content.
        """
        try:
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")
            elif not isinstance(content, str):
                raise TypeError("Content must be str or bytes")
            if max_length and len(content) > max_length:
                return f"{content[:max_length]}... [truncated]"
            return content
        except Exception as e:
            return f"[Error formatting text: {str(e)}]"


loggix = HttpResponseLogger().log_response

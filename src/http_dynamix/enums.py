"""Enumerations for various configurations and types used in the application."""

from enum import StrEnum, auto


class SegmentFormat(StrEnum):
    """Enumeration for url's segment formats."""

    CAMEL = auto()  # Use camelCase in paths
    FLAT = auto()  # Use flatcase in paths
    KEBAB = auto()  # Use kebab-case in paths
    PASCAL = auto()  # Use PascalCase in paths
    SCREAMING_SNAKE = auto()  # Use SCREAMING_SNAKE_CASE in paths
    SNAKE = auto()  # Use snake_case in paths

    DEFAULT = KEBAB


class HTTPMethod(StrEnum):
    """Enumeration for HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    TRACE = "TRACE"
    CONNECT = "CONNECT"


class ClientType(StrEnum):
    """Enumeration for client types."""

    SYNC = auto()
    ASYNC = auto()

    DEFAULT = SYNC

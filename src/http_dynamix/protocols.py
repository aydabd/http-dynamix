"""Copyright (c) 2024, Aydin A.

This module contains the protocols for the dynamic clients.
"""

from __future__ import annotations

from collections.abc import Coroutine
from typing import Any, Protocol

from http_dynamix.enums import HTTPMethod
from http_dynamix.types import Response


class SyncClientProtocol(Protocol):
    """Protocol for synchronous dynamic client."""

    def __getattr__(self, name: str) -> SyncClientProtocol:
        """Dynamic path generation."""
        ...

    def __getitem__(self, key: str | int) -> SyncClientProtocol:
        """Dynamic path generation."""
        ...

    def request(self, method: HTTPMethod, **kwargs: Any) -> Response:
        """Send a request to the server."""
        ...

    def get(self, **kwargs: Any) -> Response:
        """Send a GET request to the server."""
        ...

    def post(self, **kwargs: Any) -> Response:
        """Send a POST request to the server."""
        ...

    def put(self, **kwargs: Any) -> Response:
        """Send a PUT request to the server."""
        ...

    def delete(self, **kwargs: Any) -> Response:
        """Send a DELETE request to the server."""
        ...

    def patch(self, **kwargs: Any) -> Response:
        """Send a PATCH request to the server."""
        ...

    def head(self, **kwargs: Any) -> Response:
        """Send a HEAD request to the server."""
        ...

    def options(self, **kwargs: Any) -> Response:
        """Send an OPTIONS request to the server."""
        ...

    def trace(self, **kwargs: Any) -> Response:
        """Send a TRACE request to the server."""
        ...

    def connect(self, **kwargs: Any) -> Response:
        """Send a CONNECT request to the server."""
        ...

    def close(self) -> None:
        """Close the connection."""
        ...


class AsyncClientProtocol(Protocol):
    """Protocol for asynchronous dynamic paths."""

    def __getattr__(self, name: str) -> AsyncClientProtocol:
        """Dynamic path generation."""
        ...

    def __getitem__(self, key: str | int) -> AsyncClientProtocol:
        """Dynamic path generation."""
        ...

    async def request(
        self, method: HTTPMethod, **kwargs: Any
    ) -> Coroutine[Any, Any, Response]:
        """Send a request to the server."""
        ...

    async def get(self, **kwargs: Any) -> Coroutine[Any, Any, Response]:
        """Send a GET request to the server."""
        ...

    async def post(self, **kwargs: Any) -> Coroutine[Any, Any, Response]:
        """Send a POST request to the server."""
        ...

    async def put(self, **kwargs: Any) -> Coroutine[Any, Any, Response]:
        """Send a PUT request to the server."""
        ...

    async def delete(self, **kwargs: Any) -> Coroutine[Any, Any, Response]:
        """Send a DELETE request to the server."""
        ...

    async def patch(self, **kwargs: Any) -> Coroutine[Any, Any, Response]:
        """Send a PATCH request to the server."""
        ...

    async def head(self, **kwargs: Any) -> Coroutine[Any, Any, Response]:
        """Send a HEAD request to the server."""
        ...

    async def options(self, **kwargs: Any) -> Coroutine[Any, Any, Response]:
        """Send an OPTIONS request to the server."""
        ...

    async def trace(self, **kwargs: Any) -> Coroutine[Any, Any, Response]:
        """Send a TRACE request to the server."""
        ...

    async def connect(self, **kwargs: Any) -> Coroutine[Any, Any, Response]:
        """Send a CONNECT request to the server."""
        ...

    async def aclose(self) -> None:
        """Close the connection."""
        ...

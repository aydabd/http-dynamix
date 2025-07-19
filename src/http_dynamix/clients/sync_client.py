"""Synchronous HTTP client with dynamic path support.

This module provides a synchronous HTTP client that allows for dynamic path creation
and HTTP requests. It supports various HTTP methods and can be used in a context
manager.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx
from httpx import Response

from http_dynamix.core import PathSegment, SegmentFormatter
from http_dynamix.enums import HTTPMethod, SegmentFormat
from http_dynamix.httpx_logger import loggix
from http_dynamix.log import log as logger
from http_dynamix.protocols import SyncClientProtocol


@dataclass
class SyncDynamicClient(SyncClientProtocol):
    """Synchronous dynamic path.

    This class allows for dynamic path creation and HTTP requests.

    Example:
        .. code-block:: python

            with SyncClient("https://api.example.com") as client:
                response = client.users.john.get()
                print(response.json())
    """

    client: SyncClient
    segments: list[PathSegment] = field(default_factory=list)
    segment_format: SegmentFormat = SegmentFormat.DEFAULT
    known_paths: dict[str, str] = field(default_factory=dict)

    def _transform_path(self) -> str:
        transformed_segments = []

        for segment in self.segments:
            if segment.value is not None:
                transformed_segments.append(str(segment.value))
            else:
                segment_name = segment.name
                transformed = SegmentFormatter(
                    self.segment_format, self.known_paths
                ).transform(segment_name)
                transformed_segments.append(transformed)

        return "/".join(transformed_segments)

    def __getattr__(self, name: str) -> SyncDynamicClient:
        """Handle attribute access for dynamic path creation.

        Args:
            name: The name of the attribute.

        Returns:
            The dynamic client.
        """
        new_segments = self.segments.copy()
        new_segments.append(PathSegment(name=name, format=self.segment_format))

        return self.__class__(
            client=self.client,
            segments=new_segments,
            segment_format=self.segment_format,
            known_paths=self.known_paths,
        )

    def __getitem__(self, key: str | int | SegmentFormat) -> SyncDynamicClient:
        """Handle item access for dynamic path creation.

        Args:
            key: The key to access.

        Returns:
            The dynamic client.
        """
        if not self.segments:
            raise ValueError("Cannot use [] operator without a path segment")

        new_segments = self.segments.copy()

        # If the key is a SegmentFormat, update the last segment with the format
        if isinstance(key, SegmentFormat):
            last_segment = new_segments.pop()
            new_segments.append(last_segment.with_format(key))
        else:
            # Otherwise treat the key as a parameter value
            last_segment = new_segments.pop()
            new_segments.append(
                PathSegment(
                    name=last_segment.name, format=last_segment.format, value=key
                )
            )

        return self.__class__(
            client=self.client,
            segments=new_segments,
            segment_format=self.segment_format,
            known_paths=self.known_paths,
        )

    def with_format(self, format: SegmentFormat) -> SyncDynamicClient:
        """Set the segment format.

        Args:
            format: The segment format.

        Returns:
            The dynamic client.
        """
        return self.__class__(
            client=self.client,
            segments=self.segments,
            segment_format=format,
            known_paths=self.known_paths,
        )

    def _get_url(self) -> str:
        url = f"{self.client.base_url}/{self._transform_path()}".strip("/")
        logger.debug(f"Constructed URL: {url}")
        return str(httpx.URL(url))

    def request(
        self,
        method: HTTPMethod,
        **kwargs: Any,
    ) -> Response:
        """Make a request.

        Args:
            method: HTTP method.
            kwargs: Additional keyword arguments.

        Returns:
            Response.
        """
        url = self._get_url()

        # Remove None values
        request_kwargs = {k: v for k, v in kwargs.items() if v is not None}

        logger.debug(f"{method.value} request to {url} with {request_kwargs}")
        response = self.client._client.request(method.value, url, **request_kwargs)
        response.raise_for_status()
        loggix(response)
        return response

    def get(self, **kwargs: Any) -> Any:
        """Make a GET request.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            Response.
        """
        return self.request(HTTPMethod.GET, **kwargs)

    def post(self, **kwargs: Any) -> Any:
        """Make a POST request.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            Response.
        """
        return self.request(HTTPMethod.POST, **kwargs)

    def put(self, **kwargs: Any) -> Any:
        """Make a PUT request.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            Response.
        """
        return self.request(HTTPMethod.PUT, **kwargs)

    def delete(self, **kwargs: Any) -> Any:
        """Make a DELETE request.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            Response.
        """
        return self.request(HTTPMethod.DELETE, **kwargs)

    def patch(self, **kwargs: Any) -> Any:
        """Make a PATCH request.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            Response.
        """
        return self.request(HTTPMethod.PATCH, **kwargs)

    def head(self, **kwargs: Any) -> Any:
        """Make a HEAD request.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            Response.
        """
        return self.request(HTTPMethod.HEAD, **kwargs)

    def options(self, **kwargs: Any) -> Any:
        """Make an OPTIONS request.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            Response.
        """
        return self.request(HTTPMethod.OPTIONS, **kwargs)

    def trace(self, **kwargs: Any) -> Any:
        """Make a TRACE request.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            Response.
        """
        return self.request(HTTPMethod.TRACE, **kwargs)

    def connect(self, **kwargs: Any) -> Any:
        """Make a CONNECT request.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            Response.
        """
        return self.request(HTTPMethod.CONNECT, **kwargs)

    def close(self) -> None:
        """Close the client."""
        self.client.close()


@dataclass
class SyncClient:
    """Synchronous HTTP client.

    This class allows for making HTTP requests.

    Example:
        .. code-block:: python

            with SyncClient("https://api.example.com") as client:
                response = client.get()
                print(response.json())
    """

    base_url: str
    segment_format: SegmentFormat = SegmentFormat.DEFAULT
    known_paths: dict[str, str] = field(default_factory=dict)
    client_kwargs: dict[str, Any] = field(default_factory=dict)

    _client: httpx.Client = field(init=False)

    def __post_init__(self) -> None:
        """Initialize the client."""
        self.client_kwargs["base_url"] = self.base_url
        self._client = httpx.Client(**self.client_kwargs)

    def close(self) -> None:
        """Close the client."""
        self._client.close()

    def __enter__(self) -> SyncClient:
        """Enter the context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the context manager."""
        self.close()

    def __getattr__(self, name: str) -> SyncDynamicClient:
        """Get a dynamic client.

        Args:
            name: The name of the attribute.

        Returns:
            The dynamic client.
        """
        return SyncDynamicClient(
            client=self,
            segments=[PathSegment(name=name, format=self.segment_format)],
            segment_format=self.segment_format,
            known_paths=self.known_paths,
        )

"""Async HTTP client with dynamic path creation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Coroutine, cast

import httpx
from httpx import Response

from http_dynamix.core import PathSegment, SegmentFormatter
from http_dynamix.enums import HTTPMethod, SegmentFormat
from http_dynamix.httpx_logger import loggix
from http_dynamix.log import log as logger
from http_dynamix.protocols import AsyncClientProtocol


@dataclass
class AsyncDynamicClient(AsyncClientProtocol):
    """Asynchronous dynamic HTTP client.

    This class allows for dynamic path creation and HTTP requests.

    Example:
        .. code-block:: python

            async with AsyncClient("https://api.example.com") as client:
                response = await client.users.john.get()
                print(response.json())
    """

    client: AsyncClient
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

    def __getattr__(self, name: str) -> AsyncDynamicClient:
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

    def __getitem__(self, key: str | int | SegmentFormat) -> AsyncDynamicClient:
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

    def with_format(self, format: SegmentFormat) -> AsyncDynamicClient:
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

    async def request(
        self,
        method: HTTPMethod,
        **kwargs: Any,
    ) -> Coroutine[Any, Any, Response]:
        """Make an HTTP request.

        Args:
            method: The HTTP method to use.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        url = self._get_url()

        # Remove None values
        request_kwargs = {k: v for k, v in kwargs.items() if v is not None}

        logger.debug(f"{method.value} request to {url} with {request_kwargs!r}")
        response = await self.client._client.request(
            method.value, url, **request_kwargs
        )
        response.raise_for_status()
        loggix(response)
        return cast(Coroutine[Any, Any, Response], response)

    async def aclose(self) -> None:
        """Close the client."""
        await self.client.aclose()  # pragma: no cover

    async def get(self, **kwargs: Any) -> Any:
        """Make a GET request.

        Args:
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        return await self.request(HTTPMethod.GET, **kwargs)

    async def post(self, **kwargs: Any) -> Any:
        """Make a POST request.

        Args:
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        return await self.request(HTTPMethod.POST, **kwargs)

    async def put(self, **kwargs: Any) -> Any:
        """Make a PUT request.

        Args:
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        return await self.request(HTTPMethod.PUT, **kwargs)

    async def delete(self, **kwargs: Any) -> Any:
        """Make a DELETE request.

        Args:
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        return await self.request(HTTPMethod.DELETE, **kwargs)

    async def patch(self, **kwargs: Any) -> Any:
        """Make a PATCH request.

        Args:
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        return await self.request(HTTPMethod.PATCH, **kwargs)

    async def head(self, **kwargs: Any) -> Any:
        """Make a HEAD request.

        Args:
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        return await self.request(HTTPMethod.HEAD, **kwargs)

    async def options(self, **kwargs: Any) -> Any:
        """Make an OPTIONS request.

        Args:
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        return await self.request(HTTPMethod.OPTIONS, **kwargs)

    async def trace(self, **kwargs: Any) -> Any:
        """Make a TRACE request.

        Args:
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        return await self.request(HTTPMethod.TRACE, **kwargs)

    async def connect(self, **kwargs: Any) -> Any:
        """Make a CONNECT request.

        Args:
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        return await self.request(HTTPMethod.CONNECT, **kwargs)


@dataclass
class AsyncClient:
    """Asynchronous HTTP client.

    This class allows for making HTTP requests.

    Args:
        base_url: The base URL for the client.
        segment_format: The segment format to use.
        known_paths: A dictionary of known paths.
        client_kwargs: Additional keyword arguments to pass to the HTTP client.
    """

    base_url: str
    segment_format: SegmentFormat = SegmentFormat.DEFAULT
    known_paths: dict[str, str] = field(default_factory=dict)
    client_kwargs: dict[str, Any] = field(default_factory=dict)

    _client: httpx.AsyncClient = field(init=False)

    def __post_init__(self) -> None:
        """Initialize the HTTP client."""
        self.client_kwargs["base_url"] = self.base_url
        self._client = httpx.AsyncClient(**self.client_kwargs)

    async def aclose(self) -> None:
        """Close the client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncClient:
        """Enter the client.

        Returns:
            The client.
        """
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit the client."""
        await self.aclose()

    def __getattr__(self, name: str) -> AsyncDynamicClient:
        """Get an attribute.

        Args:
            name: The name of the attribute.

        Returns:
            The dynamic client.
        """
        return AsyncDynamicClient(
            client=self,
            segments=[PathSegment(name=name, format=self.segment_format)],
            segment_format=self.segment_format,
            known_paths=self.known_paths,
        )

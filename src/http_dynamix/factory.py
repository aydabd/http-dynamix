"""Client Factory Module for HTTP Clients.

This module provides a factory class to create synchronous or asynchronous HTTP clients
based on the specified client type. It supports both synchronous and asynchronous
operations, allowing users to choose the appropriate client for their needs.
"""

from __future__ import annotations

from typing import Any

from http_dynamix.clients import AsyncClient, SyncClient
from http_dynamix.enums import ClientType, SegmentFormat


class ClientFactory:
    """Factory to create synchronous or asynchronous clients.

    Example:
        .. code-block:: python

            # Synchronous usage
            sync_client = ClientFactory.create("https://httpbin.org")
            response = sync_client.get.get()  # GET request to https://httpbin.org/get
            print(response.json())

            # Asynchronous usage
            import asyncio


            async def main():
                async_client = ClientFactory.create(
                    https://httpbin.org",
                    ClientType.ASYNC
                )
                response = await async_client.get.get()
                print(response.json())


            asyncio.run(main())
    """

    @staticmethod
    def create(
        base_url: str,
        client_type: ClientType = ClientType.DEFAULT,
        segment_format: SegmentFormat = SegmentFormat.DEFAULT,
        known_paths: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Create a synchronous or asynchronous client.

        Args:
            base_url: The base URL for the client.
            client_type: The type of client to create.
            segment_format: The format of the path segments.
            known_paths: A dictionary of known paths.
            **kwargs: Additional keyword arguments.

        Returns:
            A synchronous or asynchronous client.
        """
        if known_paths is None:
            known_paths = {}

        match client_type:
            case ClientType.SYNC:
                return SyncClient(base_url, segment_format, known_paths, kwargs)
            case ClientType.ASYNC:
                return AsyncClient(base_url, segment_format, known_paths, kwargs)
            case _:
                return SyncClient(base_url, segment_format, known_paths, kwargs)

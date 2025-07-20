"""Authentication classes for dynamic HTTP client.

This module provides various authentication methods compatible with HTTPX client.
All authentication classes inherit from httpx.Auth and implement the required auth_flow
method for proper request authentication.
"""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Any

import httpx

from http_dynamix.log import log as logger


@dataclass(frozen=True, slots=True)
class BearerAuth(httpx.Auth):
    """Bearer token authentication method.

    Implements Bearer token authentication as defined in RFC 6750.

    Args:
        token: The bearer token for authentication.
        auth_header: Custom authorization header name (default: "Authorization").
    """

    token: str
    auth_header: str = "Authorization"

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Yields authenticated requests using Bearer auth scheme.

        Args:
            request: The HTTP request object to authenticate.

        Yields:
            httpx.Request: The authenticated HTTP request.
        """
        request.headers[self.auth_header] = self._build_auth_header()
        logger.debug("Applied Bearer token auth")
        yield request

    def _build_auth_header(self) -> str:
        """Builds the Authorization header with Bearer token.

        Returns:
            str: The formatted Authorization header.
        """
        return f"Bearer {self.token}"


@dataclass(frozen=True, slots=True)
class ApiKeyAuth(httpx.Auth):
    """API key authentication method.

    Implements API key authentication using custom header.

    Args:
        api_key: The API key for authentication.
        header_name: The header name for the API key (default: "X-API-Key").
    """

    api_key: str
    header_name: str = "X-API-Key"

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Yields authenticated requests using API key.

        Args:
            request: The HTTP request object to authenticate.

        Yields:
            httpx.Request: The authenticated HTTP request.
        """
        request.headers[self.header_name] = self.api_key
        logger.debug(f"Applied API key auth with header: {self.header_name}")
        yield request


@dataclass(slots=True)
class MultiAuth(httpx.Auth):
    """Multi-authentication method that combines multiple auth schemes.

    Allows chaining multiple authentication methods to be applied in sequence.

    Args:
        auth_methods: List of authentication methods implementing httpx.Auth.
    """

    auth_methods: list[httpx.Auth] = field(default_factory=list)

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Yields authenticated requests applying multiple auth methods.

        Applies each authentication method in sequence to the request.

        Args:
            request: The HTTP request object to authenticate.

        Yields:
            httpx.Request: The authenticated HTTP request.
        """
        current_request = request
        for auth in self.auth_methods:
            auth_flow = auth.auth_flow(current_request)
            try:
                while True:
                    current_request = next(auth_flow)
                    response = yield current_request
                    auth_flow.send(response)
            except StopIteration:
                pass
        logger.debug(f"Applied {len(self.auth_methods)} authentication methods")


# Auth-related configuration keys
AUTH_KEYS = frozenset(
    ["token", "api_key", "username", "password", "auth_header", "api_key_header"]
)


def filter_auth_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Filter kwargs to only include auth-related arguments.

    Args:
        kwargs: Original kwargs dictionary

    Returns:
        Dictionary containing only auth-related arguments
    """
    return {k: v for k, v in kwargs.items() if k in AUTH_KEYS}


def create_auth(
    token: str | None = None,
    api_key: str | None = None,
    username: str | bytes | None = None,
    password: str | bytes | None = None,
    auth_header: str = "Authorization",
    api_key_header: str = "X-API-Key",
) -> MultiAuth | None:
    """Factory function to create authentication method based on provided credentials.

    Args:
        token: Bearer token for authentication.
        api_key: API key for authentication.
        username: Username for basic authentication.
        password: Password for basic authentication.
        auth_header: Custom authorization header name (default: "Authorization").
        api_key_header: Custom API key header name (default: "X-API-Key").

    Returns:
        An instance of appropriate Auth class or None if no credentials provided.
    """
    auth_methods: list[httpx.Auth] = []

    if not any([token, api_key, username, password]):
        return None

    if token:
        auth_methods.append(BearerAuth(token=token, auth_header=auth_header))

    if api_key:
        auth_methods.append(ApiKeyAuth(api_key=api_key, header_name=api_key_header))

    if username and password:
        auth_methods.append(httpx.BasicAuth(username=username, password=password))

    return MultiAuth(auth_methods) if auth_methods else None


def prepare_auth(**kwargs: Any) -> httpx.Auth | None:
    """Prepares the authentication method for use in HTTPX client.

    Args:
        **kwargs: Keyword arguments containing authentication credentials.

    Returns:
        An instance of appropriate Auth class or None if no credentials provided.
    """
    auth_kwargs = filter_auth_kwargs(kwargs)
    auth = create_auth(**auth_kwargs)
    if auth:
        logger.debug(f"Prepared authentication: {type(auth).__name__}")
    return auth

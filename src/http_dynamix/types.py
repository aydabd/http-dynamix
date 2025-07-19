"""Type definitions for HTTP clients and responses."""

import httpx

SyncHttpClient = httpx.Client
AsyncHttpClient = httpx.AsyncClient
Response = httpx.Response

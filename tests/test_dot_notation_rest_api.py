"""Comprehensive TDD-style tests for dot-notation REST API calls.

These tests validate that the http-dynamix client can handle all types of
REST API interactions via dot notation against a mocked server.

The dot notation mechanics work as follows:

- ``client.resource`` adds a URL segment whose name is formatted and used
  directly in the path (e.g. ``client.users`` → ``/users``).
- ``client.resource.slot[value]`` adds a *value segment*: the attribute name
  (``slot``) acts as a readable placeholder, but the **value** alone appears
  in the URL (e.g. ``client.users.id[42]`` → ``/users/42``).
- Segments can be chained indefinitely to build arbitrarily deep paths
  (e.g. ``client.api.v1.users.id[42].posts.post_id[7].comments``).

Segment format transformation (``SegmentFormat``) controls how
underscore-separated attribute names are rendered in the URL:

- ``KEBAB`` (default): ``user_profile`` → ``user-profile``
- ``CAMEL``:           ``user_profile`` → ``userProfile``
- ``SNAKE``:           attribute name kept as-is (``user_profile``)
- ``PASCAL``:          ``user_profile`` → ``UserProfile``
- ``FLAT``:            ``user_profile`` → ``userprofile``
- ``SCREAMING_SNAKE``: ``user_profile`` → ``USER_PROFILE``
"""

from __future__ import annotations

import json
from datetime import timedelta

import httpx
import pytest

from http_dynamix import ClientFactory, ClientType
from http_dynamix.enums import SegmentFormat

BASE_URL = "http://api.example.com"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_transport() -> httpx.MockTransport:
    """Return a ``MockTransport`` that echoes request details as JSON."""

    def _mock_send(request: httpx.Request) -> httpx.Response:
        body: str | None = None
        if request.content:
            try:
                body = json.loads(request.content.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                body = request.content.decode(errors="replace")

        data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "params": dict(request.url.params),
            "headers": dict(request.headers),
            "body": body,
        }
        resp = httpx.Response(200, request=request, json=data)
        resp._elapsed = timedelta(0)
        return resp

    return httpx.MockTransport(_mock_send)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    """Sync client with default (kebab) segment format."""
    transport = _make_transport()
    c = ClientFactory.create(BASE_URL, transport=transport)
    yield c
    c.close()


@pytest.fixture()
def camel_client():
    """Sync client with camelCase segment format."""
    transport = _make_transport()
    c = ClientFactory.create(
        BASE_URL, transport=transport, segment_format=SegmentFormat.CAMEL
    )
    yield c
    c.close()


# ---------------------------------------------------------------------------
# GET requests
# ---------------------------------------------------------------------------


class TestGetRequests:
    """GET requests via dot notation against a mock server."""

    def test_get_collection(self, client):
        """GET /users — plain resource collection."""
        data = client.users.get().json()
        assert data["method"] == "GET"
        assert data["path"] == "/users"

    def test_get_resource_by_integer_id(self, client):
        """GET /users/42 — resource identified by integer."""
        data = client.users.id[42].get().json()
        assert data["method"] == "GET"
        assert data["path"] == "/users/42"

    def test_get_resource_by_string_id(self, client):
        """GET /users/john — resource identified by string slug."""
        data = client.users.id["john"].get().json()
        assert data["method"] == "GET"
        assert data["path"] == "/users/john"

    def test_get_nested_collection(self, client):
        """GET /users/42/posts — nested collection."""
        data = client.users.id[42].posts.get().json()
        assert data["method"] == "GET"
        assert data["path"] == "/users/42/posts"

    def test_get_deeply_nested_resource(self, client):
        """GET /users/42/posts/7/comments — three-level deep nesting."""
        data = client.users.id[42].posts.post_id[7].comments.get().json()
        assert data["method"] == "GET"
        assert data["path"] == "/users/42/posts/7/comments"

    def test_get_with_query_params(self, client):
        """GET /users?page=2&limit=25 — query string parameters."""
        data = client.users.get(params={"page": 2, "limit": 25}).json()
        assert data["method"] == "GET"
        assert data["path"] == "/users"
        assert data["params"]["page"] == "2"
        assert data["params"]["limit"] == "25"

    def test_get_with_custom_request_header(self, client):
        """GET /users with a custom header forwarded to the server."""
        data = client.users.get(
            headers={"X-Request-ID": "abc-123"}
        ).json()
        assert data["headers"]["x-request-id"] == "abc-123"

    def test_get_kebab_case_path_segment(self, client):
        """GET /response-headers — underscore attribute becomes kebab URL segment."""
        data = client.response_headers.get().json()
        assert data["path"] == "/response-headers"

    def test_get_api_versioned_path(self, client):
        """GET /api/v1/users — API version prefix chained via dot notation."""
        data = client.api.v1.users.get().json()
        assert data["path"] == "/api/v1/users"

    def test_get_deeply_versioned_nested_path(self, client):
        """GET /api/v2/users/99/settings — version + deep nesting."""
        data = client.api.v2.users.id[99].settings.get().json()
        assert data["path"] == "/api/v2/users/99/settings"


# ---------------------------------------------------------------------------
# POST requests
# ---------------------------------------------------------------------------


class TestPostRequests:
    """POST requests via dot notation against a mock server."""

    def test_post_create_resource(self, client):
        """POST /users with JSON body — create a new resource."""
        payload = {"name": "Alice", "email": "alice@example.com"}
        data = client.users.post(json=payload).json()
        assert data["method"] == "POST"
        assert data["path"] == "/users"
        assert data["body"] == payload

    def test_post_nested_resource(self, client):
        """POST /users/42/posts — create a child resource."""
        payload = {"title": "Hello World", "content": "..."}
        data = client.users.id[42].posts.post(json=payload).json()
        assert data["method"] == "POST"
        assert data["path"] == "/users/42/posts"
        assert data["body"] == payload

    def test_post_with_form_data(self, client):
        """POST /login — submit form-encoded data."""
        data = client.login.post(
            data={"username": "user", "password": "secret"}
        ).json()
        assert data["method"] == "POST"
        assert data["path"] == "/login"


# ---------------------------------------------------------------------------
# PUT requests
# ---------------------------------------------------------------------------


class TestPutRequests:
    """PUT requests via dot notation against a mock server."""

    def test_put_replace_resource(self, client):
        """PUT /users/42 — full replacement of a resource."""
        payload = {"name": "Updated Alice", "email": "alice2@example.com"}
        data = client.users.id[42].put(json=payload).json()
        assert data["method"] == "PUT"
        assert data["path"] == "/users/42"
        assert data["body"] == payload

    def test_put_nested_resource(self, client):
        """PUT /users/42/posts/7 — replace a nested resource."""
        payload = {"title": "Replaced Title"}
        data = client.users.id[42].posts.post_id[7].put(json=payload).json()
        assert data["method"] == "PUT"
        assert data["path"] == "/users/42/posts/7"
        assert data["body"] == payload


# ---------------------------------------------------------------------------
# PATCH requests
# ---------------------------------------------------------------------------


class TestPatchRequests:
    """PATCH requests via dot notation against a mock server."""

    def test_patch_partial_update(self, client):
        """PATCH /users/42 — partial update of a resource field."""
        payload = {"email": "newemail@example.com"}
        data = client.users.id[42].patch(json=payload).json()
        assert data["method"] == "PATCH"
        assert data["path"] == "/users/42"
        assert data["body"] == payload

    def test_patch_nested_settings(self, client):
        """PATCH /users/42/settings — partial update of a nested sub-resource."""
        payload = {"notifications": True}
        data = client.users.id[42].settings.patch(json=payload).json()
        assert data["method"] == "PATCH"
        assert data["path"] == "/users/42/settings"
        assert data["body"] == payload


# ---------------------------------------------------------------------------
# DELETE requests
# ---------------------------------------------------------------------------


class TestDeleteRequests:
    """DELETE requests via dot notation against a mock server."""

    def test_delete_resource(self, client):
        """DELETE /users/42 — remove a specific resource."""
        data = client.users.id[42].delete().json()
        assert data["method"] == "DELETE"
        assert data["path"] == "/users/42"

    def test_delete_nested_resource(self, client):
        """DELETE /users/42/posts/7 — remove a nested resource."""
        data = client.users.id[42].posts.post_id[7].delete().json()
        assert data["method"] == "DELETE"
        assert data["path"] == "/users/42/posts/7"


# ---------------------------------------------------------------------------
# HEAD and OPTIONS requests
# ---------------------------------------------------------------------------


class TestHeadAndOptionsRequests:
    """HEAD and OPTIONS requests via dot notation against a mock server."""

    def test_head_collection(self, client):
        """HEAD /users — check headers without body."""
        response = client.users.head()
        assert response.status_code == 200

    def test_options_collection(self, client):
        """OPTIONS /users — discover allowed methods."""
        data = client.users.options().json()
        assert data["method"] == "OPTIONS"
        assert data["path"] == "/users"

    def test_options_nested(self, client):
        """OPTIONS /users/42 — allowed methods for a specific resource."""
        data = client.users.id[42].options().json()
        assert data["method"] == "OPTIONS"
        assert data["path"] == "/users/42"


# ---------------------------------------------------------------------------
# URL segment format transformations
# ---------------------------------------------------------------------------


class TestSegmentFormats:
    """Validate all six URL segment format transformations via dot notation."""

    def test_default_kebab_format(self, client):
        """Default format converts ``user_profile`` → ``/user-profile``."""
        data = client.user_profile.get().json()
        assert data["path"] == "/user-profile"

    def test_camel_format(self, camel_client):
        """CAMEL format converts ``user_profile`` → ``/userProfile``."""
        data = camel_client.user_profile.get().json()
        assert data["path"] == "/userProfile"

    def test_snake_format(self):
        """SNAKE format keeps underscores: ``user_profile`` → ``/user_profile``."""
        transport = _make_transport()
        c = ClientFactory.create(
            BASE_URL, transport=transport, segment_format=SegmentFormat.SNAKE
        )
        data = c.user_profile.get().json()
        assert data["path"] == "/user_profile"
        c.close()

    def test_pascal_format(self):
        """PASCAL format converts ``user_profile`` → ``/UserProfile``."""
        transport = _make_transport()
        c = ClientFactory.create(
            BASE_URL, transport=transport, segment_format=SegmentFormat.PASCAL
        )
        data = c.user_profile.get().json()
        assert data["path"] == "/UserProfile"
        c.close()

    def test_flat_format(self):
        """FLAT format converts ``user_profile`` → ``/userprofile``."""
        transport = _make_transport()
        c = ClientFactory.create(
            BASE_URL, transport=transport, segment_format=SegmentFormat.FLAT
        )
        data = c.user_profile.get().json()
        assert data["path"] == "/userprofile"
        c.close()

    def test_screaming_snake_format(self):
        """SCREAMING_SNAKE format converts ``user_profile`` → ``/USER_PROFILE``."""
        transport = _make_transport()
        c = ClientFactory.create(
            BASE_URL,
            transport=transport,
            segment_format=SegmentFormat.SCREAMING_SNAKE,
        )
        data = c.user_profile.get().json()
        assert data["path"] == "/USER_PROFILE"
        c.close()

    def test_with_format_overrides_default(self, client):
        """``with_format(CAMEL)`` applied mid-chain changes subsequent formatting."""
        data = (
            client.users.id[42].with_format(SegmentFormat.CAMEL).user_profile.get().json()
        )
        assert "/users/42/userProfile" == data["path"]

    def test_per_segment_format_via_getitem(self, client):
        """``segment[SegmentFormat.CAMEL]`` formats only that segment."""
        # client.users → "users" (kebab default, single word: no change)
        # .id[42] → value "42"
        # .user_name[SegmentFormat.CAMEL] → renames segment format to camel → "userName"
        data = client.users.id[42].user_name[SegmentFormat.CAMEL].get().json()
        assert data["path"] == "/users/42/userName"

    def test_mixed_segment_values_and_formats(self, client):
        """String and integer values are passed through as-is regardless of format."""
        data = client.orgs.org["acme-corp"].repos.repo_id[7].get().json()
        assert data["path"] == "/orgs/acme-corp/repos/7"


# ---------------------------------------------------------------------------
# Known paths
# ---------------------------------------------------------------------------


class TestKnownPaths:
    """``known_paths`` lets callers pin specific path segments to exact strings."""

    def test_known_path_used_verbatim(self):
        """A segment matching a known-path key is substituted with its value."""
        transport = _make_transport()
        c = ClientFactory.create(
            BASE_URL,
            transport=transport,
            known_paths={"api_health": "health/check"},
        )
        data = c.api_health.get().json()
        assert "health/check" in data["path"]
        c.close()

    def test_known_path_combined_with_chain(self):
        """A known path can be chained with further dot-notation segments."""
        transport = _make_transport()
        c = ClientFactory.create(
            BASE_URL,
            transport=transport,
            known_paths={"api_v1": "api/v1"},
        )
        data = c.api_v1.users.get().json()
        assert data["path"] == "/api/v1/users"
        c.close()

    def test_unknown_segment_still_formatted(self):
        """Segments not in known_paths are still format-transformed normally."""
        transport = _make_transport()
        c = ClientFactory.create(
            BASE_URL,
            transport=transport,
            known_paths={"api_v1": "api/v1"},
            segment_format=SegmentFormat.CAMEL,
        )
        data = c.api_v1.user_profile.get().json()
        assert data["path"] == "/api/v1/userProfile"
        c.close()


# ---------------------------------------------------------------------------
# Async client
# ---------------------------------------------------------------------------


class TestAsyncDotNotation:
    """Async client mirrors the sync dot notation API with ``await``."""

    @pytest.mark.asyncio
    async def test_async_get_collection(self):
        """Async GET /users."""
        transport = _make_transport()
        async with ClientFactory.create(
            BASE_URL, client_type=ClientType.ASYNC, transport=transport
        ) as c:
            data = (await c.users.get()).json()
        assert data["method"] == "GET"
        assert data["path"] == "/users"

    @pytest.mark.asyncio
    async def test_async_get_resource_by_id(self):
        """Async GET /users/42."""
        transport = _make_transport()
        async with ClientFactory.create(
            BASE_URL, client_type=ClientType.ASYNC, transport=transport
        ) as c:
            data = (await c.users.id[42].get()).json()
        assert data["path"] == "/users/42"

    @pytest.mark.asyncio
    async def test_async_post_create_resource(self):
        """Async POST /users with a JSON body."""
        transport = _make_transport()
        payload = {"name": "Bob"}
        async with ClientFactory.create(
            BASE_URL, client_type=ClientType.ASYNC, transport=transport
        ) as c:
            data = (await c.users.post(json=payload)).json()
        assert data["method"] == "POST"
        assert data["path"] == "/users"
        assert data["body"] == payload

    @pytest.mark.asyncio
    async def test_async_put_replace_resource(self):
        """Async PUT /users/1."""
        transport = _make_transport()
        payload = {"name": "Updated Bob"}
        async with ClientFactory.create(
            BASE_URL, client_type=ClientType.ASYNC, transport=transport
        ) as c:
            data = (await c.users.id[1].put(json=payload)).json()
        assert data["method"] == "PUT"
        assert data["path"] == "/users/1"

    @pytest.mark.asyncio
    async def test_async_patch_partial_update(self):
        """Async PATCH /users/1."""
        transport = _make_transport()
        payload = {"email": "bob@example.com"}
        async with ClientFactory.create(
            BASE_URL, client_type=ClientType.ASYNC, transport=transport
        ) as c:
            data = (await c.users.id[1].patch(json=payload)).json()
        assert data["method"] == "PATCH"
        assert data["path"] == "/users/1"

    @pytest.mark.asyncio
    async def test_async_delete_resource(self):
        """Async DELETE /users/1."""
        transport = _make_transport()
        async with ClientFactory.create(
            BASE_URL, client_type=ClientType.ASYNC, transport=transport
        ) as c:
            data = (await c.users.id[1].delete()).json()
        assert data["method"] == "DELETE"
        assert data["path"] == "/users/1"

    @pytest.mark.asyncio
    async def test_async_deeply_nested_resource(self):
        """Async GET /users/42/posts/7/comments."""
        transport = _make_transport()
        async with ClientFactory.create(
            BASE_URL, client_type=ClientType.ASYNC, transport=transport
        ) as c:
            data = (await c.users.id[42].posts.post_id[7].comments.get()).json()
        assert data["path"] == "/users/42/posts/7/comments"

    @pytest.mark.asyncio
    async def test_async_segment_format_camel(self):
        """Async client respects CAMEL segment format."""
        transport = _make_transport()
        async with ClientFactory.create(
            BASE_URL,
            client_type=ClientType.ASYNC,
            transport=transport,
            segment_format=SegmentFormat.CAMEL,
        ) as c:
            data = (await c.user_profile.get()).json()
        assert data["path"] == "/userProfile"

    @pytest.mark.asyncio
    async def test_async_with_query_params(self):
        """Async GET /users?page=1&limit=5."""
        transport = _make_transport()
        async with ClientFactory.create(
            BASE_URL, client_type=ClientType.ASYNC, transport=transport
        ) as c:
            data = (await c.users.get(params={"page": 1, "limit": 5})).json()
        assert data["params"]["page"] == "1"
        assert data["params"]["limit"] == "5"

    @pytest.mark.asyncio
    async def test_async_head_request(self):
        """Async HEAD /users."""
        transport = _make_transport()
        async with ClientFactory.create(
            BASE_URL, client_type=ClientType.ASYNC, transport=transport
        ) as c:
            response = await c.users.head()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_async_options_request(self):
        """Async OPTIONS /users."""
        transport = _make_transport()
        async with ClientFactory.create(
            BASE_URL, client_type=ClientType.ASYNC, transport=transport
        ) as c:
            data = (await c.users.options()).json()
        assert data["method"] == "OPTIONS"

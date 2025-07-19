"""Tests for synchronous and asynchronous HTTP clients using httpbin.org."""
import pytest
from http_dynamix import ClientFactory, ClientType, SegmentFormat


HTTPBIN_URL = "http://httpbin.org"

@pytest.fixture
def httpbin_sync_client():
    """Fixture for creating a synchronous HTTP client for httpbin.org."""
    client = ClientFactory.create(HTTPBIN_URL)
    yield client
    client.close()


class TestHttpbinClient:
    """Tests for the synchronous HTTP client using httpbin.org."""

    @pytest.mark.parametrize("params, status_code", [
        ({"freeform": "test"}, 200)
    ])
    def test_sync_client_get(self, httpbin_sync_client, params, status_code):
        response = httpbin_sync_client.response_headers.get(params=params)
        assert response.status_code == status_code

    def test_sync_client_nested_post(self, httpbin_sync_client):
        expected_status_code = 200
        response = httpbin_sync_client.post.post()
        assert response.status_code == expected_status_code

    def test_sync_client_nested_get(self, httpbin_sync_client):
        expected_status_code = 200
        response = httpbin_sync_client.get.get()
        assert response.status_code == expected_status_code

    def test_sync_client_path_attr(self, httpbin_sync_client):
        expected_status_code = 200
        response = httpbin_sync_client.status.status[200].get()
        assert response.status_code == expected_status_code


class TestHttpbinAsyncClient:
    """Tests for the asynchronous HTTP client using httpbin.org."""

    @pytest.mark.asyncio
    async def test_async_client(self):
        expected_status_code = 200

        async with ClientFactory.create(HTTPBIN_URL, client_type=ClientType.ASYNC) as httpbin_async_client:
            response = await httpbin_async_client.response_headers.get(params={"freeform": "test"})
            assert response.status_code == expected_status_code

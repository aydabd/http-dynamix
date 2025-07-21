"""Integration tests for HTTP Dynamix using httpbin.org."""
import pytest
import pytest_asyncio
from http_dynamix import ClientFactory, ClientType, SegmentFormat

@pytest.fixture
def httpbin_client():
    """Create a test client for httpbin.org."""
    client = ClientFactory.create(
        "https://httpbin.org",
        client_type=ClientType.SYNC,
        segment_format=SegmentFormat.KEBAB,
    )
    yield client
    client.close()

@pytest_asyncio.fixture
async def async_httpbin_client():
    """Create an async test client for httpbin.org."""
    client = ClientFactory.create(
        "https://httpbin.org",
        client_type=ClientType.ASYNC,
        segment_format=SegmentFormat.KEBAB,
    )
    yield client
    await client.aclose()

@pytest.mark.httpbin
class TestHttpbinIntegration:
    """Test HTTP Dynamix integration with httpbin.org."""

    def test_get_request(self, httpbin_client):
        """Test GET request."""
        response = httpbin_client.get.get()
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://httpbin.org/get"

    def test_post_with_json(self, httpbin_client):
        """Test POST request with JSON data."""
        test_data = {"key": "value"}
        response = httpbin_client.post.post(json=test_data)
        assert response.status_code == 200
        data = response.json()
        assert data["json"] == test_data

    def test_base64_endpoint(self, httpbin_client):
        """Test base64 endpoint."""
        import base64
        value = "SFRUUEJJTiBpcyBhd2Vzb21l"  # base64 for 'HTTPBIN is awesome'
        response = httpbin_client.base64.base64[value].get()
        assert response.status_code == 200
        # The response should be the decoded value
        assert response.text == base64.b64decode(value).decode()

    @pytest.mark.asyncio
    async def test_async_get_request(self, async_httpbin_client):
        """Test async GET request."""
        response = await async_httpbin_client.get.get()
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://httpbin.org/get"

    @pytest.mark.asyncio
    async def test_async_post_with_json(self, async_httpbin_client):
        """Test async POST request with JSON data."""
        test_data = {"key": "value"}
        response = await async_httpbin_client.post.post(json=test_data)
        assert response.status_code == 200
        data = response.json()
        assert data["json"] == test_data

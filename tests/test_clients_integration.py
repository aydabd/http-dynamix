import pytest
import pytest_asyncio
import httpx
from http_dynamix import ClientFactory, ClientType

HTTPBIN_URL = "https://httpbin.org"

@pytest.fixture(scope="module")
def sync_client():
    client = ClientFactory.create(HTTPBIN_URL)
    yield client
    client.close()

@pytest.mark.parametrize("endpoint,method,params", [
    ("get", "get", {"foo": "bar"}),
    ("post", "post", {"foo": "bar"}),
    ("put", "put", {"foo": "bar"}),
    ("delete", "delete", None),
    ("patch", "patch", {"foo": "bar"}),
])
def test_sync_client_httpbin(sync_client, endpoint, method, params):
    client = getattr(sync_client, endpoint)
    response = getattr(client, method)(params=params if params else None)
    assert response.status_code in (200, 201, 204)
    assert response.url.host == "httpbin.org"

def test_sync_client_head(sync_client):
    response = sync_client.get.head()
    assert response.status_code == 200

def test_sync_client_options(sync_client):
    response = sync_client.get.options()
    assert response.status_code == 200

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="function")
async def async_client():
    client = ClientFactory.create(HTTPBIN_URL, client_type=ClientType.ASYNC)
    yield client
    await client.aclose()

@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,method,params", [
    ("get", "get", {"foo": "bar"}),
    ("post", "post", {"foo": "bar"}),
    ("put", "put", {"foo": "bar"}),
    ("delete", "delete", None),
    ("patch", "patch", {"foo": "bar"}),
])
async def test_async_client_httpbin(async_client, endpoint, method, params):
    client_endpoint = getattr(async_client, endpoint)
    response = await getattr(client_endpoint, method)(params=params if params else None)
    assert response.status_code in (200, 201, 204)
    assert response.url.host == "httpbin.org"

@pytest.mark.asyncio
async def test_async_client_head(async_client):
    response = await async_client.get.head()
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_async_client_options(async_client):
    response = await async_client.get.options()
    assert response.status_code == 200

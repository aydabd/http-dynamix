import pytest
import httpx

from http_dynamix import ClientFactory, ClientType

BASE_URL = "http://test"


from datetime import timedelta


def _mock_send(request: httpx.Request) -> httpx.Response:
    response = httpx.Response(200, request=request, json={"url": str(request.url)})
    response._elapsed = timedelta(0)
    return response


@pytest.fixture()
def sync_client():
    transport = httpx.MockTransport(_mock_send)
    client = ClientFactory.create(BASE_URL, transport=transport)
    yield client
    client.close()


class TestSyncClient:
    @pytest.mark.parametrize("segment,param", [
        ("response_headers", {"freeform": "test"}),
    ])
    def test_sync_client_get(self, sync_client, segment, param):
        response = getattr(sync_client, segment).get(params=param)
        assert response.status_code == 200
        assert "/response-headers" in response.json()["url"]

    def test_sync_client_nested_post(self, sync_client):
        response = sync_client.post.post()
        assert response.status_code == 200
        assert "/post" in response.json()["url"]

    def test_sync_client_nested_get(self, sync_client):
        response = sync_client.get.get()
        assert response.status_code == 200
        assert "/get" in response.json()["url"]

    def test_sync_client_path_attr(self, sync_client):
        response = sync_client.status.status[200].get()
        assert response.status_code == 200
        assert "/status/200" in response.json()["url"]


class TestAsyncClient:
    @pytest.mark.asyncio
    async def test_async_client(self):
        transport = httpx.MockTransport(_mock_send)
        async with ClientFactory.create(BASE_URL, client_type=ClientType.ASYNC, transport=transport) as client:
            resp = await client.response_headers.get(params={"freeform": "test"})
            assert resp.status_code == 200
            assert "/response-headers" in resp.json()["url"]


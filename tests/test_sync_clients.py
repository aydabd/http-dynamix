import pytest
import httpx
from http_dynamix import ClientFactory, ClientType
from http_dynamix.clients.sync_client import SyncClient, SyncDynamicClient
from http_dynamix.core import PathSegment
from http_dynamix.enums import SegmentFormat
from datetime import timedelta

BASE_URL = "http://test"

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

    def test_syncclient_close(self):
        c = SyncClient("http://test")
        c.close()  # Should not raise

    def test_syncclient_context_manager(self):
        c = SyncClient("http://test")
        with c as client:
            assert client is c
        c.close()

class TestSyncDynamicClient:
    def test_getitem_no_segments(self):
        client = SyncDynamicClient(client=None, segments=[])
        with pytest.raises(ValueError):
            client["anything"]

    def test_getitem_with_segment_format(self):
        client = SyncDynamicClient(client=None, segments=[PathSegment("foo")])
        new_client = client[SegmentFormat.CAMEL]
        assert new_client.segments[-1].format == SegmentFormat.CAMEL

    def test_getitem_with_value_str(self):
        client = SyncDynamicClient(client=None, segments=[PathSegment("foo")])
        new_client = client["bar"]
        assert new_client.segments[-1].value == "bar"

    def test_getitem_with_value_int(self):
        client = SyncDynamicClient(client=None, segments=[PathSegment("foo")])
        new_client = client[123]
        assert new_client.segments[-1].value == 123

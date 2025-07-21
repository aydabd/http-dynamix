import pytest
import httpx
from http_dynamix import ClientFactory, ClientType
from http_dynamix.clients.async_client import AsyncClient, AsyncDynamicClient
from http_dynamix.core import PathSegment
from http_dynamix.enums import SegmentFormat
from datetime import timedelta

BASE_URL = "http://test"

def _mock_send(request: httpx.Request) -> httpx.Response:
    response = httpx.Response(200, request=request, json={"url": str(request.url)})
    response._elapsed = timedelta(0)
    return response

class TestAsyncClient:
    @pytest.mark.asyncio
    async def test_async_client(self):
        transport = httpx.MockTransport(_mock_send)
        async with ClientFactory.create(BASE_URL, client_type=ClientType.ASYNC, transport=transport) as client:
            resp = await client.response_headers.get(params={"freeform": "test"})
            assert resp.status_code == 200
            assert "/response-headers" in resp.json()["url"]

class TestAsyncDynamicClient:
    @pytest.mark.asyncio
    async def test_getitem_no_segments(self):
        client = AsyncDynamicClient(client=None, segments=[])
        with pytest.raises(ValueError):
            client["anything"]

    @pytest.mark.asyncio
    async def test_aclose(self):
        c = AsyncClient("http://test")
        await c.aclose()  # Should not raise

    @pytest.mark.asyncio
    async def test_context_manager(self):
        c = AsyncClient("http://test")
        async with c as client:
            assert client is c
        await c.aclose()

    def test_getitem_with_segment_format(self):
        client = AsyncDynamicClient(client=None, segments=[PathSegment("foo")])
        new_client = client[SegmentFormat.CAMEL]
        assert new_client.segments[-1].format == SegmentFormat.CAMEL

    def test_getitem_with_value_str(self):
        client = AsyncDynamicClient(client=None, segments=[PathSegment("foo")])
        new_client = client["bar"]
        assert new_client.segments[-1].value == "bar"

    def test_getitem_with_value_int(self):
        client = AsyncDynamicClient(client=None, segments=[PathSegment("foo")])
        new_client = client[123]
        assert new_client.segments[-1].value == 123

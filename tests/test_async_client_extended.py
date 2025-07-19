import pytest
import httpx
from datetime import timedelta

from http_dynamix import ClientFactory, ClientType, SegmentFormat
from http_dynamix.clients.async_client import AsyncDynamicClient


def _mock_send(request: httpx.Request) -> httpx.Response:
    resp = httpx.Response(200, request=request, json={"url": str(request.url)})
    resp._elapsed = timedelta(0)
    return resp


@pytest.mark.asyncio
async def test_async_client_methods_and_paths():
    transport = httpx.MockTransport(_mock_send)
    async with ClientFactory.create("http://x", client_type=ClientType.ASYNC, transport=transport) as client:
        dynamic = client.users["john"].posts[123]
        assert isinstance(dynamic, AsyncDynamicClient)
        dynamic = dynamic.with_format(SegmentFormat.SNAKE)
        assert dynamic.segment_format == SegmentFormat.SNAKE
        assert (await dynamic.get()).status_code == 200
        await dynamic.post()
        await dynamic.put()
        await dynamic.delete()
        await dynamic.patch()
        await dynamic.head()
        await dynamic.options()
        await dynamic.trace()
        await dynamic.connect()


def test_async_dynamic_client_index_error():
    transport = httpx.MockTransport(_mock_send)
    client = ClientFactory.create("http://x", client_type=ClientType.ASYNC, transport=transport)
    empty_dynamic = AsyncDynamicClient(client=client, segments=[], segment_format=SegmentFormat.DEFAULT)
    with pytest.raises(ValueError):
        _ = empty_dynamic["val"]

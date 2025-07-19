import httpx

from http_dynamix import ClientFactory, ClientType, SegmentFormat


def _mock_send(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, request=request)


def test_factory_creates_clients():
    transport = httpx.MockTransport(_mock_send)
    sync = ClientFactory.create("http://x", transport=transport)
    assert sync.base_url == "http://x"

    async_client = ClientFactory.create(
        "http://x", client_type=ClientType.ASYNC, segment_format=SegmentFormat.SNAKE, transport=transport
    )
    assert async_client.base_url == "http://x"
    assert async_client.segment_format == SegmentFormat.SNAKE


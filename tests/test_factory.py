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
    from http_dynamix.clients.async_client import AsyncClient

    assert isinstance(async_client, AsyncClient)


def test_factory_sync_type():
    transport = httpx.MockTransport(_mock_send)
    sync = ClientFactory.create("http://x", client_type=ClientType.SYNC, transport=transport)
    from http_dynamix.clients.sync_client import SyncClient

    assert isinstance(sync, SyncClient)


def test_factory_unknown_type():
    class DummyType:
        pass

    transport = httpx.MockTransport(_mock_send)
    sync = ClientFactory.create("http://x", client_type=DummyType(), transport=transport)
    from http_dynamix.clients.sync_client import SyncClient

    assert isinstance(sync, SyncClient)


def test_factory_async_type_with_none_known_paths():
    transport = httpx.MockTransport(_mock_send)
    async_client = ClientFactory.create(
        "http://x", client_type=ClientType.ASYNC, known_paths=None, transport=transport
    )
    from http_dynamix.clients.async_client import AsyncClient

    assert isinstance(async_client, AsyncClient)
    assert async_client.known_paths == {}

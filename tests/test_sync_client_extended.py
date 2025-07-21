import httpx
from datetime import timedelta

from http_dynamix import ClientFactory, SegmentFormat
from http_dynamix.clients.sync_client import SyncDynamicClient


def _mock_send(request: httpx.Request) -> httpx.Response:
    resp = httpx.Response(200, request=request, json={"url": str(request.url)})
    resp._elapsed = timedelta(0)
    return resp


def test_sync_client_methods_and_paths():
    transport = httpx.MockTransport(_mock_send)
    client = ClientFactory.create("http://x", transport=transport)
    dynamic = client.users["john"].posts[123]
    assert isinstance(dynamic, SyncDynamicClient)
    dynamic = dynamic.with_format(SegmentFormat.CAMEL)
    assert dynamic.segment_format == SegmentFormat.CAMEL
    assert dynamic.get().status_code == 200
    dynamic.post()
    dynamic.put()
    dynamic.delete()
    dynamic.patch()
    dynamic.head()
    dynamic.options()
    dynamic.trace()
    dynamic.connect()
    client.close()


def test_sync_dynamic_client_index_error():
    transport = httpx.MockTransport(_mock_send)
    client = ClientFactory.create("http://x", transport=transport)
    empty_dynamic = SyncDynamicClient(client=client, segments=[], segment_format=SegmentFormat.DEFAULT)
    try:
        _ = empty_dynamic["val"]
    except ValueError:
        pass

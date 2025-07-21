import pytest
import httpx

from http_dynamix.auth import (
    BearerAuth,
    ApiKeyAuth,
    MultiAuth,
    filter_auth_kwargs,
    create_auth,
    prepare_auth,
)


def test_bearer_auth_flow():
    auth = BearerAuth(token="t")
    req = httpx.Request("GET", "http://x")
    flow = auth.auth_flow(req)
    result = next(flow)
    assert result.headers["Authorization"] == "Bearer t"
    with pytest.raises(StopIteration):
        next(flow)


def test_api_key_auth_flow():
    auth = ApiKeyAuth(api_key="k", header_name="X-API-Key")
    req = httpx.Request("GET", "http://x")
    result = next(auth.auth_flow(req))
    assert result.headers["X-API-Key"] == "k"


def test_multi_auth_flow():
    auth = MultiAuth([BearerAuth("t"), ApiKeyAuth("k")])
    req = httpx.Request("GET", "http://x")
    flow = auth.auth_flow(req)
    first = next(flow)
    assert first.headers["Authorization"] == "Bearer t"
    second = flow.send(httpx.Response(200, request=first))
    assert second.headers["X-API-Key"] == "k"
    with pytest.raises(StopIteration):
        flow.send(httpx.Response(200, request=second))


def test_filter_and_prepare():
    kwargs = {"token": "t", "api_key": "k", "other": 1}
    filtered = filter_auth_kwargs(kwargs)
    assert filtered == {"token": "t", "api_key": "k"}
    auth = create_auth(**filtered)
    assert isinstance(auth, MultiAuth)
    prepared = prepare_auth(**kwargs)
    assert isinstance(prepared, MultiAuth)


def test_create_auth_none():
    assert create_auth() is None


def test_create_auth_token_only():
    auth = create_auth(token="t")
    assert isinstance(auth, MultiAuth)
    assert len(auth.auth_methods) == 1
    assert isinstance(auth.auth_methods[0], BearerAuth)


def test_create_auth_api_key_only():
    auth = create_auth(api_key="k")
    assert isinstance(auth, MultiAuth)
    assert len(auth.auth_methods) == 1
    assert isinstance(auth.auth_methods[0], ApiKeyAuth)


def test_create_auth_basic_only():
    auth = create_auth(username="u", password="p")
    assert isinstance(auth, MultiAuth)
    assert len(auth.auth_methods) == 1
    assert isinstance(auth.auth_methods[0], httpx.BasicAuth)


def test_create_auth_basic_missing_username():
    auth = create_auth(password="p")
    assert auth is None


def test_create_auth_basic_missing_password():
    auth = create_auth(username="u")
    assert auth is None


def test_prepare_auth_none():
    assert prepare_auth() is None


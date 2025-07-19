import httpx

from datetime import timedelta

from http_dynamix.httpx_logger import HttpResponseLogger, JsonFormatter


def test_httpx_logger_logs_response(caplog):
    logger = HttpResponseLogger()
    response = httpx.Response(
        200,
        request=httpx.Request("GET", "http://x"),
        headers={"content-type": "application/json"},
        json={"foo": "bar"},
    )
    response._elapsed = timedelta(0)
    logger.log_response(response)


def test_httpx_logger_get_formatter():
    logger = HttpResponseLogger()
    assert isinstance(logger._get_formatter("application/json"), JsonFormatter)
    resp = httpx.Response(200, request=httpx.Request("GET", "http://x"), text="hi")
    resp._elapsed = timedelta(0)
    assert 'binary' in logger._format_content(resp)


from http_dynamix.httpx_logger import (
    JsonFormatter,
    XmlFormatter,
    HtmlFormatter,
    CsvFormatter,
    BinaryFormatter,
    FormDataFormatter,
    YamlFormatter,
)


def test_formatters_work():
    assert "foo" in JsonFormatter().format('{"foo": 1}')
    assert "bar" in XmlFormatter().format("<bar></bar>")
    assert "<html" in HtmlFormatter().format("<html></html>")
    assert "|" in CsvFormatter().format("a,b\nc,d")
    data = BinaryFormatter(include_content=True).format(b"binary")
    assert "size" in data and "content" in data
    content = b"--boundary\r\nX: y\r\n\r\nval\r\n--boundary--\r\n"
    assert "Binary" not in FormDataFormatter().format(content)
    assert "foo" in YamlFormatter().format("foo: bar")

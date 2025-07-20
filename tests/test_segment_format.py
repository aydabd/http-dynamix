import pytest
from http_dynamix.core import PathSegment, SegmentFormatter
from http_dynamix.enums import SegmentFormat


def test_path_segment_str_and_with_format():
    seg = PathSegment("user_id", SegmentFormat.SNAKE)
    assert str(seg) == "user_id"

    new = seg.with_format(SegmentFormat.CAMEL)
    assert new.format == SegmentFormat.CAMEL

    seg2 = PathSegment("id", value=5)
    assert str(seg2) == "5"


def test_segment_formatter_cases():
    f = SegmentFormatter(SegmentFormat.CAMEL)
    assert f.camel_case("hello_world") == "helloWorld"
    assert f.flat_case("hello_world") == "helloworld"
    assert f.kebab_case("hello_world") == "hello-world"
    assert f.pascal_case("hello_world") == "HelloWorld"
    assert f.screaming_snake_case("hello_world") == "HELLO_WORLD"
    assert f.snake_case("hello-World") == "hello_world"


def test_segment_formatter_transform():
    known = {"special": "known"}
    f = SegmentFormatter(SegmentFormat.PASCAL, known)
    assert f.transform("special") == "known"
    assert f.transform("hello_world") == "HelloWorld"


@pytest.mark.parametrize("fmt,inp,expected", [
    (SegmentFormat.CAMEL, "foo_bar", "fooBar"),
    (SegmentFormat.FLAT, "foo_bar", "foobar"),
    (SegmentFormat.KEBAB, "foo_bar", "foo-bar"),
    (SegmentFormat.PASCAL, "foo_bar", "FooBar"),
    (SegmentFormat.SCREAMING_SNAKE, "foo_bar", "FOO_BAR"),
    (SegmentFormat.SNAKE, "foo-bar", "foo_bar"),
])
def test_transform_all_cases(fmt, inp, expected):
    f = SegmentFormatter(fmt)
    assert f.transform(inp) == expected


def test_transform_default_branch():
    class DummyFormat:
        pass
    f = SegmentFormatter(DummyFormat)
    assert f.transform("foo_bar") == "foo-bar"  # kebab_case fallback


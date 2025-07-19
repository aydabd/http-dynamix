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


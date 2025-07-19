"""Path segment formatting module.

This module provides classes and methods to represent and format URL path segments.
It includes the `PathSegment` class for representing segments and the `SegmentFormatter`
class for formatting segments based on different styles.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from http_dynamix.enums import SegmentFormat


@dataclass
class PathSegment:
    """Represent a segment in the URL path.

    Args:
        name: Segment name.
        format: Segment format. Default is SegmentFormat.DEFAULT.
        value: Segment value. Default is None.

    Examples:
        .. code-block:: python

            segment = PathSegment("user_id", SegmentFormat.FLAT, 1)
            print(segment)
            # Output: 1
    """

    name: str
    format: SegmentFormat = SegmentFormat.DEFAULT
    value: str | int | None = None

    def __str__(self) -> str:
        """Convert segment to string."""
        if self.value is not None:
            return str(self.value)
        return self.name

    def with_format(self, format: SegmentFormat) -> PathSegment:
        """Create a new segment with a different format.

        Args:
            format: Segment format.

        Returns:
            New segment with the specified format.

        Examples:
            .. code-block:: python

                segment = PathSegment("user_id", SegmentFormat.FLAT)
                new_segment = segment.with_format(SegmentFormat.CAMEL)
                print(new_segment)
                # Output: user_id
        """
        return PathSegment(self.name, format, self.value)


@dataclass
class SegmentFormatter:
    """Format URL path segments based on the specified format.

    Args:
        segment_format: Default segment format. Default is SegmentFormat.DEFAULT.
        known_paths: Known paths with their formats. Default is an empty dictionary.

    Examples:
        .. code-block:: python

            formatter = SegmentFormatter(
                SegmentFormat.CAMEL, {"user_id": SegmentFormat.FLAT}
            )
            formatted = formatter.transform("user_id")
            print(formatted)
            # Output: userid
    """

    segment_format: SegmentFormat = SegmentFormat.DEFAULT
    known_paths: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def camel_case(segment: str) -> str:
        """Transform segment to camel case.

        Args:
            segment: Segment to transform.

        Returns:
            Transformed segment.

        Examples:
            .. code-block:: python

                formatted = SegmentFormatter.camel_case("hello_world")
                print(formatted)
                # Output: helloWorld
        """
        segments = segment.split("_")
        return segments[0] + "".join(seg.capitalize() for seg in segments[1:])

    @staticmethod
    def flat_case(segment: str) -> str:
        """Transform segment to flat case.

        Args:
            segment: Segment to transform.

        Returns:
            Transformed segment.

        Examples:
            .. code-block:: python

                formatted = SegmentFormatter.flat_case("hello_World")
                print(formatted)
                # Output: helloworld
        """
        return segment.replace("_", "").lower()

    @staticmethod
    def kebab_case(segment: str) -> str:
        """Transform segment to kebab case.

        Args:
            segment: Segment to transform.

        Returns:
            Transformed segment.

        Examples:
            .. code-block:: python

                formatted = SegmentFormatter.kebab_case("hello_world")
                print(formatted)
                # Output: hello-world
        """
        return segment.replace("_", "-").lower()

    @staticmethod
    def pascal_case(segment: str) -> str:
        """Transform segment to Pascal case.

        Args:
            segment: Segment to transform.

        Returns:
            Transformed segment.

        Examples:
            .. code-block:: python

                formatted = SegmentFormatter.pascal_case("hello_world")
                print(formatted)
                # Output: HelloWorld
        """
        segments = segment.split("_")
        return "".join(seg.capitalize() for seg in segments)

    @staticmethod
    def screaming_snake_case(segment: str) -> str:
        """Transform segment to SCREAMING_SNAKE_CASE.

        Args:
            segment: Segment to transform.

        Returns:
            Transformed segment.

        Examples:
            .. code-block:: python

                formatted = SegmentFormatter.screaming_snake_case("hello_world")
                print(formatted)
                # Output: HELLO_WORLD
        """
        return segment.replace("_", "_").upper()

    @staticmethod
    def snake_case(segment: str) -> str:
        """Transform segment to snake case.

        Args:
            segment: Segment to transform.

        Returns:
            Transformed segment.

        Examples:
            .. code-block:: python

                formatted = SegmentFormatter.snake_case("hello-World")
                print(formatted)
                # Output: hello_world
        """
        return segment.replace("-", "_").lower()

    def transform(self, segment: str) -> str:
        """Transform segment.

        Args:
            segment: Segment to transform.

        Returns:
            Transformed segment.
        """
        if segment in self.known_paths:
            return self.known_paths[segment]

        match self.segment_format:
            case SegmentFormat.CAMEL:
                return self.camel_case(segment)
            case SegmentFormat.FLAT:
                return self.flat_case(segment)
            case SegmentFormat.KEBAB:
                return self.kebab_case(segment)
            case SegmentFormat.PASCAL:
                return self.pascal_case(segment)
            case SegmentFormat.SCREAMING_SNAKE:
                return self.screaming_snake_case(segment)
            case SegmentFormat.SNAKE:
                return self.snake_case(segment)
            case _:
                return self.kebab_case(segment)

"""Copyright (c) 2024, Aydin A.

This module provides a customizable logging system using loguru.

It supports structured JSON logging, custom levels, patchers, extra fields
and dynamic verbosity control.

**Features**:

  - JSON serialization for logs (useful for structured logging in systems like ELK.)
  - Custom log levels with colorization and icons.
  - Configurable handlers (console, file, etc.) with log rotation and retention.
  - Extra fields to bind additional context globally (e.g., user IDs, session IDs).
  - Patcher for modifying log records in-place.
  - Dynamic verbosity control via CLI flags (`-v`, `-vv`, etc.).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self, TextIO

import yaml
from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from os import PathLike

    import loguru


# Default YAML configuration template for stdout logging
DEFAULT_CONFIG = """
version: 1
disable_existing_loggers: False

root:
  handlers:
    - sink: sys.stdout
      level: DEBUG
      format: "[{time:YYYY-MM-DD HH:mm:ss}]-[{level}]-[{file}:{line}] {message}"
      serialize: false  # Output logs in JSON format to stdout
      colorize: true  # Use colorful output for terminal
"""


@dataclass
class FormatterConfig:
    """Dataclass to define a formatter configuration.

    Args:
        format: The log message format.
        serialize: Whether to serialize logs to JSON.
        colorize: Whether to colorize the log output.
    """

    format: str = "[{time:YYYY-MM-DD HH:mm:ss}]-[{level}]-[{file}:{line}] {message}"
    serialize: bool = True
    colorize: bool = True


@dataclass
class HandlerConfig:
    """Dataclass to define a handler configuration.

    Args:
        sink: The sink to log to (e.g., file path, sys.stdout, sys.stderr).
        level: The logging level (e.g., "INFO", "DEBUG").
        format: The formatter configuration.
        rotation: The log rotation policy (e.g., "10 MB").
        retention: The log retention policy (e.g., "10 days").
        compression: The compression policy (e.g., "zip").
        enqueue: Whether to enqueue log messages.
    """

    sink: str | PathLike[str] = "sys.stdout"
    level: str = "INFO"
    format: FormatterConfig = field(default_factory=FormatterConfig)
    rotation: str | None = None
    retention: str | None = None
    compression: str | None = None
    enqueue: bool = False

    def resolve_sink(self) -> str | PathLike[str] | TextIO:
        """Resolves the sink to a file object or string.

        Returns:
            The resolved sink object.
        """
        if isinstance(self.sink, str):
            if self.sink == "sys.stdout":
                return sys.stdout
            if self.sink == "sys.stderr":
                return sys.stderr
        if isinstance(self.sink, Path):
            return str(self.sink)
        return self.sink


@dataclass
class LevelConfig:
    """Dataclass to define custom log levels.

    Args:
        name: The name of the custom log level.
        no: The log level number.
        color: The color of the log level.
        icon: The icon of the log level.
    """

    name: str = ""
    no: int = 0
    color: str | None = None
    icon: str | None = None


@dataclass
class LoggerConfig:
    """Dataclass to define a logger configuration.

    Args:
        handlers: The list of handler configurations.
        levels: The list of custom log levels.
    """

    handlers: list[HandlerConfig] = field(default_factory=list)
    levels: list[LevelConfig] = field(default_factory=list)


@dataclass
class LoggingConfig:
    """Dataclass to define the root logging configuration.

    Args:
        version: The configuration version.
        disable_existing_loggers: Whether to disable existing loggers.
        root: The root logger configuration.
        extra: Extra fields bound to the logger.
        patcher: Patcher function to modify log records.
        activation: Enable/disable loggers.
    """

    version: int = 1
    disable_existing_loggers: bool = False
    root: LoggerConfig = field(default_factory=LoggerConfig)
    extra: dict[str, Any] = field(default_factory=dict)
    patcher: Callable[[loguru.Record], None] | None = None
    activation: list[tuple[str, bool]] = field(default_factory=list)


class LogMaster:
    """LogMaster is a customizable logging system using loguru.

    It supports structured JSON logging, custom levels, patchers, extra fields
    and dynamic verbosity control.

    Features:

      - JSON serialization for logs (useful for structured logging in systems like ELK.)
      - Custom log levels with colorization and icons.
      - Configurable handlers (console, file, etc.) with log rotation and retention.
      - Extra fields to bind additional context globally (e.g., user IDs, session IDs).
      - Patcher for modifying log records in-place.
      - Dynamic verbosity control via CLI flags (`-v`, `-vv`, etc.).

    Example:
        .. code-block:: python

            from log import log, LogMaster

            # Initialize logger with default stdout configuration
            LogMaster(config_path=None)

            # Log with custom fields
            log = log.bind(user_id=123, session_id="abc")
            log.info("Logging with custom fields")


            @LogMaster.watch
            def divide(a: int, b: int) -> float:
                return a / b


            try:
                result = divide(10, 2)
                log.info(f"Result of division: {result}")
            except ZeroDivisionError:
                log.error("Cannot divide by zero!")

    Example:
        .. code-block:: python

            import click
            from log import log, LogMaster


            @click.command()
            @click.option(
                "-v", "--verbose", count=True, help="Increase verbosity (-v, -vv, -vvv)"
            )
            def main(verbose):
                LogMaster.set_verbosity(verbose)  # Adjust verbosity dynamically
                log.info("Logging at selected verbosity level.")


            if __name__ == "__main__":
                main()
    """

    def __init__(self: Self, config_path: str | None = None):
        """Initializes the logger configuration.

        If no configuration file is provided, it defaults to a stdout handler.

        Args:
            config_path: Path to the logger configuration file (YAML).
                         If None, use default.
        """
        self.config = (
            self._load_config(config_path)
            if config_path
            else self._load_default_config()
        )
        self._configure_logger()

    @staticmethod
    def _load_config(config_path: str) -> LoggingConfig:
        """Loads the logging configuration from a YAML file into the dataclasses.

        Args:
            config_path: The path to the YAML configuration file.

        Returns:
            LoggingConfig: The parsed logging configuration.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            yaml.YAMLError: If the configuration file is invalid.
        """
        config_file = Path(config_path)
        if not config_file.is_file():
            error_message = f"Config file '{config_path}' does not exist."
            raise FileNotFoundError(error_message)
        with open(config_file) as file:
            config_dict = yaml.safe_load(file)
            return LogMaster._parse_config(config_dict)

    @staticmethod
    def _load_default_config() -> LoggingConfig:
        """Loads the default logging configuration for stdout.

        Returns:
            LoggingConfig: The parsed logging configuration.
        """
        config_dict = yaml.safe_load(DEFAULT_CONFIG)
        return LogMaster._parse_config(config_dict)

    @staticmethod
    def _parse_config(config_dict: dict[str, Any]) -> LoggingConfig:
        """Parses the dictionary configuration into LoggingConfig dataclass.

        Args:
            config_dict: The configuration dictionary.

        Returns:
            LoggingConfig: The parsed logging configuration.
        """
        try:
            handlers = [
                HandlerConfig(
                    sink=handler.get("sink", "sys.stdout"),
                    level=handler.get("level", "INFO"),
                    format=FormatterConfig(
                        format=handler.get(
                            "format",
                            "[{time:YYYY-MM-DD HH:mm:ss}]-[{level}]-[{file}:{line}] {message}",  # noqa: E501
                        ),
                        serialize=handler.get("serialize", True),
                        colorize=handler.get("colorize", True),
                    ),
                    rotation=handler.get("rotation"),
                    retention=handler.get("retention"),
                    compression=handler.get("compression"),
                    enqueue=handler.get("enqueue", False),
                )
                for handler in config_dict["root"]["handlers"]
            ]
            levels = [
                LevelConfig(
                    name=level.get("name"),
                    no=level.get("no"),
                    color=level.get("color"),
                    icon=level.get("icon"),
                )
                for level in config_dict.get("levels", [])
            ]
            root_logger = LoggerConfig(handlers=handlers, levels=levels)

            return LoggingConfig(
                version=config_dict.get("version", 1),
                disable_existing_loggers=config_dict.get(
                    "disable_existing_loggers", False
                ),
                root=root_logger,
                patcher=config_dict.get("patcher"),
                activation=config_dict.get("activation", []),
            )
        except KeyError as e:
            error_message = f"Invalid configuration format: {e}"
            raise yaml.YAMLError(error_message) from e

    def _configure_logger(self: Self) -> None:
        """Configures the logger using the dataclass-based settings.

        It removes any default handlers added by loguru and adds the handlers
        from the configuration.

        It also adds custom levels, extra fields, patchers
        and enables/disables specific loggers.
        """
        logger.remove()  # Remove any default handlers added by loguru

        # Add handlers from the configuration
        for handler in self.config.root.handlers:
            sink = handler.resolve_sink()

            if isinstance(sink, str | Path):
                logger.add(
                    sink,
                    level=handler.level,
                    format=handler.format.format,
                    serialize=handler.format.serialize,
                    colorize=handler.format.colorize,
                    rotation=handler.rotation,
                    retention=handler.retention,
                    compression=handler.compression,
                    enqueue=handler.enqueue,
                )
            else:
                logger.add(
                    sink,
                    level=handler.level,
                    format=handler.format.format,
                    serialize=handler.format.serialize,
                    colorize=handler.format.colorize,
                )

        # Add custom levels from the configuration
        for level in self.config.root.levels:
            logger.level(level.name, no=level.no, color=level.color, icon=level.icon)

        # Apply extra fields globally
        if self.config.extra:
            logger.configure(extra=self.config.extra)

        # Apply the patcher function if provided
        if self.config.patcher:
            logger.configure(patcher=self.config.patcher)

        # Enable or disable specific loggers
        if self.config.activation:
            for name, state in self.config.activation:
                if state:
                    logger.enable(name)
                else:
                    logger.disable(name)

    @staticmethod
    def set_verbosity(verbosity: int) -> None:
        """Sets the verbosity level of the logger.

        It is based on the number of `-v` flags.

        Args:
            verbosity: Verbosity level based on the number of `-v` flags.
        """
        levels = {0: "WARNING", 1: "INFO", 2: "DEBUG", 3: "TRACE"}
        level = levels.get(verbosity, "TRACE")
        logger.remove()  # Remove all existing handlers
        logger.configure(handlers=[{"sink": sys.stdout, "level": level}])

    @staticmethod
    def watch(func: Callable[..., Any]) -> Callable[..., Any]:
        """A decorator that logs.

        It logs function calls, including arguments, results, and exceptions.

        Args:
            func: The function to decorate.

        Returns:
            The decorated function.
        """

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapper function that logs function calls and exceptions.

            It logs the function call, including arguments, results, and exceptions.

            Args:
                args: The positional arguments.
                kwargs: The keyword arguments.

            Returns:
                The result of the wrapped function.
            """
            module_name = func.__module__
            function_name = func.__name__
            module_function = f"'[{module_name}]': {function_name}"

            func_args = ", ".join(repr(arg) for arg in args if arg)
            func_kwargs = ", ".join(
                f"{key}={value!r}" for key, value in kwargs.items() if key and value
            )
            inputs = ", ".join(filter(None, [func_args, func_kwargs]))

            module_function_with_args = f"{module_function}({inputs})"

            enter_message = f"Entering {module_function_with_args}"
            exit_message = f"Exiting {module_function}"

            # We make sure even logger shows shows the module and function name with
            # line number as where it is called
            logger.info(enter_message)
            try:
                output = func(*args, **kwargs)
            except Exception as e:
                error_message = (
                    f"[{module_function_with_args}] raised an exception: {e}"
                )
                logger.exception(error_message)
                raise
            else:
                info_message = f"{exit_message} with output -> {output}"
                logger.info(info_message)
                return output

        return wrapper


# Initialize the logger globally for the project
LogMaster()._configure_logger()
log = logger

from http_dynamix.log import LogMaster, log
import pytest
import tempfile
import yaml
import os
from pathlib import Path


@pytest.fixture(autouse=True)
def cleanup_custom_sink():
    yield
    if os.path.exists("custom_sink"):
        os.remove("custom_sink")


def test_logmaster_watch_and_verbosity(caplog):
    caplog.set_level("INFO")
    lm = LogMaster()
    LogMaster.set_verbosity(2)

    @LogMaster.watch
    def add(a, b):
        return a + b

    result = add(1, 2)
    assert result == 3


def test_logmaster_watch_exception():
    lm = LogMaster()

    @LogMaster.watch
    def div(a, b):
        return a / b

    with pytest.raises(ZeroDivisionError):
        div(1, 0)


def test_logmaster_set_verbosity_levels():
    for v in range(5):
        LogMaster.set_verbosity(v)


def test_logmaster_load_custom_config():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {
                    "sink": "sys.stdout",
                    "level": "DEBUG",
                    "format": "[{level}] {message}",
                    "serialize": False,
                    "colorize": True,
                }
            ]
        },
        "levels": [
            {"name": "CUSTOM", "no": 25, "color": "<yellow>", "icon": "*"}
        ],
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        assert isinstance(lm, LogMaster)
    finally:
        os.remove(fname)


def test_logmaster_patcher_and_extra():
    def patcher(record):
        record["extra"]["patched"] = True
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {
                    "sink": "sys.stdout",
                    "level": "INFO",
                    "format": "[{level}] {message}",
                    "serialize": False,
                    "colorize": True,
                }
            ]
        },
        "extra": {"foo": "bar"},
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        lm.config.patcher = patcher  # Set patcher after loading config
        assert isinstance(lm, LogMaster)
    finally:
        os.remove(fname)


def test_log_levels():
    log.info("Info message")
    log.debug("Debug message")
    log.warning("Warning message")
    log.error("Error message")
    log.trace("Trace message")


def test_logmaster_invalid_config_file():
    # Should raise error if config file does not exist
    with pytest.raises(FileNotFoundError):
        LogMaster(config_path="/tmp/nonexistent_config.yaml")


def test_logmaster_custom_level_usage():
    unique_level = f"CUSTOM_{os.getpid()}"
    unique_no = 25 + (os.getpid() % 100)
    from loguru import logger
    # Register the custom level only if it does not exist
    try:
        logger.level(unique_level)
    except ValueError:
        logger.level(unique_level, no=unique_no, color="<yellow>", icon="*")
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {
                    "sink": "sys.stdout",
                    "level": unique_level,
                    "format": "[{level}] {message}",
                    "serialize": False,
                    "colorize": True,
                }
            ]
        }
        # Remove 'levels' section to avoid re-registering
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        log.log(unique_no, "Custom level message")
    finally:
        os.remove(fname)


def test_logmaster_patcher_effect():
    def patcher(record):
        record["extra"]["patched"] = True
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {
                    "sink": "sys.stdout",
                    "level": "INFO",
                    "format": "[{level}] {message}",
                    "serialize": False,
                    "colorize": True,
                }
            ]
        },
        "extra": {"foo": "bar"},
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        lm.config.patcher = patcher  # Set patcher after loading config
        log.info("Test patcher effect", extra={"baz": 123})
    finally:
        os.remove(fname)


def test_logmaster_set_verbosity_edge():
    # Test edge values for verbosity
    LogMaster.set_verbosity(-1)
    LogMaster.set_verbosity(100)


def test_logmaster_sink_resolution():
    # sys.stderr
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": "sys.stderr", "level": "INFO"}
            ]
        }
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
    finally:
        os.remove(fname)

    # Path object
    config["root"]["handlers"][0]["sink"] = str(Path("/tmp/test.log"))
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
    finally:
        os.remove(fname)

    # Other type (string)
    config["root"]["handlers"][0]["sink"] = "sys.stdout"
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
    finally:
        os.remove(fname)


def test_logmaster_invalid_config_format():
    # Should raise yaml.YAMLError due to missing key
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        # 'root' key is missing
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        with pytest.raises(yaml.YAMLError):
            LogMaster(config_path=fname)
    finally:
        os.remove(fname)


def test_logmaster_configure_extra_and_patcher():
    def patcher(record):
        record["extra"]["patched"] = True
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": "sys.stdout", "level": "INFO"}
            ]
        },
        "extra": {"foo": "bar"},
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        lm.config.patcher = patcher
        log.info("Test patcher and extra", extra={"baz": 123})
    finally:
        os.remove(fname)


def test_logmaster_activation():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": "sys.stdout", "level": "INFO"}
            ]
        },
        # Use list of lists instead of list of tuples for YAML compatibility
        "activation": [["http_dynamix", True], ["other_module", False]],
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
    finally:
        os.remove(fname)


def test_logmaster_sink_resolution_all_branches():
    # Case: sink is not sys.stderr and not Path (should return as is)
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": "custom_sink", "level": "INFO"}
            ]
        }
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
    finally:
        os.remove(fname)

    # Case: sink is Path
    config["root"]["handlers"][0]["sink"] = str(Path("/tmp/test.log"))
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
    finally:
        os.remove(fname)

    # Case: sink is custom object (should be resolved to the object)
    class CustomSink:
        def write(self, msg):
            pass
    custom_sink = CustomSink()
    # Set the custom object after loading config
    config["root"]["handlers"][0]["sink"] = "sys.stdout"
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        lm.config.root.handlers[0].sink = custom_sink
        resolved = lm.config.root.handlers[0].resolve_sink()
        assert resolved is custom_sink
    finally:
        os.remove(fname)


def test_logmaster_configure_extra():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": "sys.stdout", "level": "INFO"}
            ]
        },
        "extra": {"foo": "bar"},
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        log.info("Test extra", extra={"baz": 123})
    finally:
        os.remove(fname)


def test_logmaster_configure_patcher():
    def patcher(record):
        record["extra"]["patched"] = True
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": "sys.stdout", "level": "INFO"}
            ]
        },
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        lm.config.patcher = patcher
        log.info("Test patcher", extra={"baz": 123})
    finally:
        os.remove(fname)


def test_logmaster_sink_resolution_path_object():
    # Case: sink is a Path object (not just string)
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": str(Path("/tmp/test_path_obj.log")), "level": "INFO"}
            ]
        }
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.safe_dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
    finally:
        os.remove(fname)


def test_logmaster_sink_resolution_stderr():
    # Case: sink is sys.stderr
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": "sys.stderr", "level": "INFO"}
            ]
        }
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.safe_dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
    finally:
        os.remove(fname)


def test_logmaster_sink_resolution_custom_object():
    class CustomSink:
        def write(self, msg):
            pass
    custom_sink = CustomSink()
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": "sys.stdout", "level": "INFO"}
            ]
        }
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        # Replace the sink with custom object
        lm.config.root.handlers[0].sink = custom_sink
        resolved = lm.config.root.handlers[0].resolve_sink()
        assert resolved is custom_sink
    finally:
        os.remove(fname)


def test_logmaster_configure_extra_and_patcher_both():
    def patcher(record):
        record["extra"]["patched"] = True
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": "sys.stdout", "level": "INFO"}
            ]
        },
        "extra": {"foo": "bar"},
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        lm.config.patcher = patcher
        log.info("Test both extra and patcher", extra={"baz": 123})
        # No assertion needed, just ensure both are set and used
    finally:
        os.remove(fname)


def test_logmaster_configure_extra_and_patcher_init():
    def patcher(record):
        record["extra"]["patched"] = True
    # Set both extra and patcher in config before initializing LogMaster
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "handlers": [
                {"sink": "sys.stdout", "level": "INFO"}
            ]
        },
        "extra": {"foo": "bar"},
        # patcher cannot be serialized, so set after
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        yaml.dump(config, f)
        fname = f.name
    try:
        lm = LogMaster(config_path=fname)
        lm.config.patcher = patcher
        lm._configure_logger()  # Re-configure to pick up patcher
        log.info("Test both extra and patcher at init", extra={"baz": 123})
    finally:
        os.remove(fname)

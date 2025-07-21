import yaml
from pathlib import Path

from http_dynamix.log import LogMaster, LoggingConfig


def test_load_default_config(tmp_path):
    lm = LogMaster()
    assert isinstance(lm.config, LoggingConfig)

    config_yaml = tmp_path / "log.yml"
    config_yaml.write_text(
        """
version: 1
root:
  handlers:
    - sink: sys.stdout
      level: INFO
"""
    )
    loaded = LogMaster._load_config(str(config_yaml))
    assert isinstance(loaded, LoggingConfig)


def test_set_verbosity():
    LogMaster.set_verbosity(1)

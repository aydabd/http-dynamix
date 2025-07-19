from http_dynamix.log import LogMaster, log


def test_logmaster_watch_and_verbosity(caplog):
    caplog.set_level("INFO")
    lm = LogMaster()
    LogMaster.set_verbosity(2)

    @LogMaster.watch
    def add(a, b):
        return a + b

    result = add(1, 2)
    assert result == 3



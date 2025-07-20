import pytest
from click.testing import CliRunner

import httpx

@pytest.mark.parametrize(
    "args,expected_status,expected_in_output",
    [
        (["https://httpbin.org/get"], 200, "url"),
        (["--method", "POST", "https://httpbin.org/post"], 200, "form"),
        (["https://httpbin.org/base64/SFRUUEJJTiBpcyBhd2Vzb21l"], 200, "HTTPBIN is awesome"),
    ],
)
def test_httpx_cli(args, expected_status, expected_in_output):
    runner = CliRunner()
    result = runner.invoke(httpx.main, args)
    assert result.exit_code == 0
    assert str(expected_status) in result.output
    assert expected_in_output in result.output

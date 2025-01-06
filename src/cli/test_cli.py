import sys
import pytest
from src.cli.cli import main as cli_main
import subprocess


@pytest.mark.parametrize("falcon_config, empire_config, expected_return", [
    ("./examples/example4/millennium-falcon.json", "./examples/example4/empire.json", 100),  
])
def test_cli_main_success(monkeypatch, falcon_config, empire_config, expected_return, capsys):
    """
    Test the CLI by mocking sys.argv and calling `main()` directly.
    `capsys` captures stdout/stderr for verification.
    """

    monkeypatch.setattr(sys, "argv", ["give-me-the-odds", falcon_config, empire_config])

    cli_main()

    captured = capsys.readouterr()
    try:
        odds_result = int(captured.out.strip())
    except ValueError:
        pytest.fail(f"CLI did not print an integer. Output was: {captured.out}")

    assert odds_result == expected_return, (
        f"Expected odds {expected_return} but got {odds_result}. "
        f"CLI output: {captured.out}"
    )


def test_cli_main_file_missing(monkeypatch, capsys):
    """
    Test behavior when passing a non-existing file path.
    We expect the CLI to print an error message and exit(1).
    """
    falcon_config = "does_not_exist_millennium-falcon.json"
    empire_config = "does_not_exist_empire.json"

    # Mock sys.argv
    monkeypatch.setattr(sys, "argv", ["give-me-the-odds", falcon_config, empire_config])

    with pytest.raises(SystemExit) as exc_info:
        cli_main()

    assert exc_info.value.code == 1, "CLI should exit with code 1 on error"

    captured = capsys.readouterr()
    assert "An error occurred:" in captured.out


@pytest.mark.parametrize("falcon_config, empire_config", [
    ("./examples/example4/millennium-falcon.json", "./examples/example4/empire.json"),
])
def test_cli_subprocess_success(falcon_config, empire_config):
    """
    Example test that runs the CLI as if from a shell.
    Needs the package  `give-me-the-odds` to be installed using `pip install -e .` to run successfully.
    """
    # Assume 'give-me-the-odds' is on the system PATH after installing via setup.py
    cmd = ["give-me-the-odds", falcon_config, empire_config]

    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode == 0, (
        f"CLI returned error code {result.returncode}. "
        f"stderr: {result.stderr}"
    )

    try:
        odds_result = int(result.stdout.strip())
    except ValueError:
        pytest.fail(f"CLI did not print a valid integer. Output: {result.stdout}")

    assert odds_result == 100, (
        f"Expected odds 100 for example4, got {odds_result}.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )


def test_cli_subprocess_missing_files():
    """
    Example test with non-existing files using subprocess.
    Expect an error code and some 'An error occurred' in output.
    """
    cmd = ["give-me-the-odds", "not_found_millennium-falcon.json", "not_found_empire.json"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode == 1, "CLI should exit with code 1 when files are missing"
    assert "An error occurred:" in result.stdout or result.stderr

import subprocess
from approvaltests import verify
import pytest

# Test the CLI with no arguments (should show help or default output)
def test_cli_no_args():
    result = subprocess.run([
        "python", "-m", "rotate"
    ], capture_output=True, text=True)
    verify(result.stdout)

# Test the CLI with --help (should show help output)
def test_cli_help():
    result = subprocess.run([
        "python", "-m", "rotate", "--help"
    ], capture_output=True, text=True)
    verify(result.stdout)

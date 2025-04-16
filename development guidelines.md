# testing

- prefer pytest
- prefer approvaltests over asserts
- use the native reporter to see mismatches on cli

## Running the tests

To run all tests (including ApprovalTests with the native reporter), use:

```bash
pytest -v
```

If an approval test fails, you can approve the new output by running the command printed in the test output (usually a `mv` command).
- prefer inline approvals if output not too long (less than 10 line)

## Running the CLI

To execute the CLI, you have two main options:

**1. Run as a module (recommended):**

```bash
python -m rotate.cli <command> [options]
```
Example:
```bash
python -m rotate.cli init -y
```

**2. Run the script directly:**

```bash
python rotate/cli.py <command> [options]
```

Replace `<command>` with any of the available subcommands (e.g., `init`, `start`, `stop`, etc.). Use `-y` or `--yes` for non-interactive initialization.
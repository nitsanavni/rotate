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
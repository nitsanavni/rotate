# Progress Checklist

- [x] Decide on the programming language and initial project structure for implementing the `rotate` CLI tool, based on the spec in `spec.md`.

  - **Language Chosen:** Python
  - **Rationale:** Python is cross-platform, easy to distribute, and well-suited for CLI tools involving file I/O, timers, and process management. It is also accessible for contributors and rapid prototyping.
  - **Initial Project Structure:**
    ```
    rotate/
    ├── rotate/               # Python package with CLI source code
    │   ├── __main__.py       # Entry point for CLI (`python -m rotate`)
    │   ├── cli.py            # CLI argument parsing and command dispatch
    │   ├── rotation.py       # Core logic for rotation, timer, file I/O
    │   └── hooks.py          # Hook execution logic
    ├── tests/                # Unit tests
    │   └── test_rotation.py
    ├── .rotate/              # Created at runtime for session state and hooks
    │   ├── rotation          # The rotation state file
    │   └── hooks/            # Directory for hook scripts
    ├── requirements.txt      # Python dependencies
    ├── README.md             # Project overview and usage
    ├── setup.py              # For pip installation (optional)
    └── progress.md           # Progress tracking
    ```

- [x] Implement the CLI entry point and argument parsing:
  - Created `rotate/__main__.py` to allow running `python -m rotate`.
  - Created `rotate/cli.py` to parse commands (`init`, `start`, `stop`, `rotate`, `randomize`, `watch`, `open`) and dispatch to appropriate functions (currently as stubs).

- [ ] Add tests, specifically to test the CLI default output:
  - Write tests that invoke the CLI with no arguments and with basic commands, verifying that the output matches the expected default/help output as described in the spec.

# Rotate Project Guidelines

## Commands
- **Run**: `python -m main` or `python main.py`
- **Test**: `pytest` or `pytest -xvs tests/` (when tests are added)
- **Lint**: `ruff check .`
- **Format**: `black .`
- **Type Check**: `mypy .`

## Code Style Guidelines
- **Python Version**: 3.12+
- **Formatting**: Follow Black code style with default settings
- **Linting**: Use Ruff for linting and error detection
- **Imports**: 
  - Group by standard library, third-party, local imports
  - Sort alphabetically within groups
- **Type Hints**: Use type annotations for all function parameters and return types
- **Naming**:
  - Use snake_case for variables, functions, and methods
  - Use CamelCase for classes
  - Use UPPER_CASE for constants
- **Documentation**: Document public functions and classes with docstrings
- **Error Handling**: Use appropriate exception handling with specific exception types
- **State Management**: Keep file operations atomic to prevent corruption

## Project Structure
- Use modular design following the architecture specified in spec.md
- Implement components (CLI, Timer Daemon, State Management, IPC, Hooks) separately
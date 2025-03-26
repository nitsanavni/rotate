#!/usr/bin/env python
import os
import subprocess
import sys
from typing import List


def get_rotate_directory() -> str:
    """Return the path to the .rotate directory."""
    return os.path.join(os.getcwd(), ".rotate")


def get_hooks_directory() -> str:
    """Return the path to the hooks directory."""
    return os.path.join(get_rotate_directory(), "hooks")


def ensure_rotate_directory_exists() -> str:
    """Ensure the .rotate directory exists, add .gitignore, and return its path."""
    rotate_dir = get_rotate_directory()
    os.makedirs(rotate_dir, exist_ok=True)

    # Create .gitignore file to prevent committing .rotate contents
    gitignore_path = os.path.join(rotate_dir, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("*\n")

    return rotate_dir


def ensure_hooks_directory_exists() -> str:
    """Ensure the hooks directory exists and return its path."""
    # First ensure parent .rotate directory exists with .gitignore
    ensure_rotate_directory_exists()

    # Then create hooks subdirectory
    hooks_dir = get_hooks_directory()
    os.makedirs(hooks_dir, exist_ok=True)
    return hooks_dir


def list_hooks(event_name: str) -> List[str]:
    """List all hook scripts for a specific event."""
    hooks_dir = get_hooks_directory()
    if not os.path.exists(hooks_dir):
        return []

    # Find exact match for event name
    event_hook_path = os.path.join(hooks_dir, event_name)
    if os.path.exists(event_hook_path) and os.access(event_hook_path, os.X_OK):
        return [event_hook_path]

    return []


def execute_hooks(event_name: str) -> None:
    """Execute all hooks for the given event."""
    hooks = list_hooks(event_name)
    if not hooks:
        print(f"No hooks found for event: {event_name}")
        return

    print(f"Executing {len(hooks)} hook(s) for event '{event_name}'...")

    for hook_path in hooks:
        try:
            print(f"Running hook: {hook_path}")
            # Run the hook as a detached process so it doesn't block the daemon
            subprocess.Popen(
                hook_path,
                start_new_session=True,  # Disown the process
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
            print(f"Hook started: {hook_path}")
        except Exception as e:
            print(f"Error executing hook '{hook_path}': {e}")


def main():
    """CLI entry point for testing hooks."""
    if len(sys.argv) < 2:
        print("Usage: python hooks.py <event_name>")
        sys.exit(1)

    event_name = sys.argv[1]
    execute_hooks(event_name)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
import os
from typing import Optional


def get_ipc_file_path(rotation_file_path: str) -> str:
    """Generate the IPC file path based on the rotation file path.

    Args:
        rotation_file_path: Path to the rotation file

    Returns:
        Path to the IPC file
    """
    return f"{rotation_file_path}.ipc"


def write_command(rotation_file_path: str, command: str) -> None:
    """Write a command to the IPC file.

    Args:
        rotation_file_path: The path to the rotation file
        command: The command to write to the IPC file
    """
    ipc_file_path = get_ipc_file_path(rotation_file_path)
    with open(ipc_file_path, "w") as f:
        f.write(command)


def read_command(rotation_file_path: str) -> Optional[str]:
    """Read a command from the IPC file and delete it.

    Args:
        rotation_file_path: The path to the rotation file

    Returns:
        The command from the IPC file, or None if the file doesn't exist
    """
    ipc_file_path = get_ipc_file_path(rotation_file_path)

    if not os.path.exists(ipc_file_path):
        return None

    try:
        with open(ipc_file_path, "r") as f:
            command = f.read().strip()

        # Delete the file after reading
        os.unlink(ipc_file_path)
        return command
    except Exception:
        return None


def cleanup_ipc_file(rotation_file_path: str) -> None:
    """Clean up any existing IPC file.

    Args:
        rotation_file_path: The path to the rotation file
    """
    ipc_file_path = get_ipc_file_path(rotation_file_path)
    if os.path.exists(ipc_file_path):
        os.unlink(ipc_file_path)

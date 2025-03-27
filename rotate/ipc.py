#!/usr/bin/env python
import os
from typing import Optional


def get_ipc_file_path(rotation_file_path: str) -> str:
    return f"{rotation_file_path}.ipc"


def write_command(rotation_file_path: str, command: str) -> None:
    ipc_file_path = get_ipc_file_path(rotation_file_path)
    with open(ipc_file_path, "w") as f:
        f.write(command)


def read_command(rotation_file_path: str) -> Optional[str]:
    ipc_file_path = get_ipc_file_path(rotation_file_path)

    if not os.path.exists(ipc_file_path):
        return None

    try:
        with open(ipc_file_path, "r") as f:
            command = f.read().strip()

        os.unlink(ipc_file_path)
        return command
    except Exception:
        return None


def cleanup_ipc_file(rotation_file_path: str) -> None:
    ipc_file_path = get_ipc_file_path(rotation_file_path)
    if os.path.exists(ipc_file_path):
        os.unlink(ipc_file_path)

#!/usr/bin/env python
import os
import sys
import subprocess
from typing import List
from rotate.parse import parse_rotation_file, format_rotation, Rotation


def read_rotation_file(file_path: str) -> Rotation:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Rotation file not found: {file_path}")

    with open(file_path, "r") as f:
        content = f.read()

    return parse_rotation_file(content)


def write_rotation_file(file_path: str, rotation: Rotation) -> None:
    formatted = format_rotation(rotation)
    with open(file_path, "w") as f:
        f.write(formatted)


def create_rotation_file(
    file_path: str, team_members: List[str], initial_time: str = "5:00"
) -> None:
    if os.path.exists(file_path):
        raise FileExistsError(f"File already exists: {file_path}")

    with open(file_path, "w") as f:
        f.write(f"{initial_time} / {initial_time}\n")
        if len(team_members) > 0:
            f.write(f"Typing: {team_members[0]}\n")
        if len(team_members) > 1:
            f.write(f"Talking: {team_members[1]}\n")
        if len(team_members) > 2:
            f.write(f"Next: {team_members[2]}\n")

        for member in team_members[3:]:
            f.write(f"{member}\n")


def cat_rotation_file(file_path: str) -> None:
    """Display the content of the rotation file to stdout."""
    try:
        # Read and print file content
        with open(file_path, "r") as f:
            content = f.read()

        print(content, end="")
    except FileNotFoundError:
        print(f"Error: Rotation file not found: {file_path}")
    except Exception as e:
        print(f"Error reading rotation file: {e}")


def open_rotation_file(file_path: str) -> None:
    """Open the rotation file in the default editor."""
    # Check if rotation file exists
    if not os.path.exists(file_path):
        print(f"Error: Rotation file not found: {file_path}")
        return

    try:
        # Determine editor to use
        editor = os.environ.get("EDITOR", os.environ.get("VISUAL", None))

        if editor:
            # Use specified editor from environment variable
            subprocess.Popen([editor, file_path])
            print(f"Opened {file_path} with {editor}")
        else:
            # Try to use platform-specific open command
            if sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", file_path])
            elif sys.platform == "win32":  # Windows
                os.startfile(file_path)
            else:  # Linux/Unix
                subprocess.Popen(["xdg-open", file_path])

            print(f"Opened {file_path} with default application")
    except Exception as e:
        print(f"Error opening rotation file: {e}")

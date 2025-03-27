#!/usr/bin/env python
import os
from typing import List
from rotate.parse import parse_rotation_file, format_rotation, Rotation


def read_rotation_file(file_path: str) -> Rotation:
    """Read and parse a rotation file into a Rotation object.

    Args:
        file_path: The path to the rotation file

    Returns:
        A Rotation object parsed from the file

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file contents can't be parsed
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Rotation file not found: {file_path}")

    with open(file_path, "r") as f:
        content = f.read()

    return parse_rotation_file(content)


def write_rotation_file(file_path: str, rotation: Rotation) -> None:
    """Write a Rotation object to a file.

    Args:
        file_path: The path where the rotation file should be written
        rotation: The Rotation object to write
    """
    formatted = format_rotation(rotation)
    with open(file_path, "w") as f:
        f.write(formatted)


def create_rotation_file(
    file_path: str, team_members: List[str], initial_time: str = "5:00"
) -> None:
    """Create a new rotation file.

    Args:
        file_path: The path where the rotation file should be written
        team_members: List of team member names
        initial_time: The initial timer value (default: "5:00")

    Raises:
        FileExistsError: If the file already exists
    """
    if os.path.exists(file_path):
        raise FileExistsError(f"File already exists: {file_path}")

    # Create rotation file
    with open(file_path, "w") as f:
        f.write(f"{initial_time} / {initial_time}\n")
        if len(team_members) > 0:
            f.write(f"Typing: {team_members[0]}\n")
        if len(team_members) > 1:
            f.write(f"Talking: {team_members[1]}\n")
        if len(team_members) > 2:
            f.write(f"Next: {team_members[2]}\n")

        # Add remaining team members
        for member in team_members[3:]:
            f.write(f"{member}\n")

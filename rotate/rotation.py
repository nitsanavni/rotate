#!/usr/bin/env python
import os
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

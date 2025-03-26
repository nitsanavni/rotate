#!/usr/bin/env python
import sys
import json
import re
from datetime import time
from typing import List
from dataclasses import dataclass, field


@dataclass
class Timer:
    remaining: time
    total: time

    def __str__(self) -> str:
        return f"{time_to_str(self.remaining)} / {time_to_str(self.total)}"


@dataclass
class Rotation:
    timer: Timer
    positions: List[str] = field(default_factory=list)
    team: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert Rotation object to dictionary for JSON serialization."""
        return {
            "timer": {
                "remaining": time_to_str(self.timer.remaining),
                "total": time_to_str(self.timer.total),
            },
            "positions": self.positions,
            "team": self.team,
        }


def parse_time(time_str: str) -> time:
    """Parse a time string in format MM:SS to a time object."""
    try:
        minutes, seconds = map(int, time_str.split(":"))
        return time(hour=0, minute=minutes, second=seconds)
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}")


def time_to_str(t: time) -> str:
    """Convert a time object to MM:SS format."""
    return f"{t.minute}:{t.second:02d}"


def parse_timer_line(line: str) -> Timer:
    """Parse the timer line format 'remaining / total'."""
    match = re.match(r"(\d+:\d+)\s*/\s*(\d+:\d+)", line)
    if not match:
        raise ValueError(f"Invalid timer format: {line}")

    remaining_str, total_str = match.groups()
    remaining = parse_time(remaining_str)
    total = parse_time(total_str)
    return Timer(remaining=remaining, total=total)


def parse_rotation_file(content: str) -> Rotation:
    """Parse the rotation file content into a Rotation object."""
    lines = content.strip().split("\n")

    if not lines:
        raise ValueError("Empty rotation file")

    # Parse timer line (first line)
    timer = parse_timer_line(lines[0])

    positions = []
    team = []

    # Parse positions and team members
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        # Check if line defines a position
        position_match = re.match(r"(\w+):\s*(.+)", line)
        if position_match:
            position, name = position_match.groups()
            positions.append(position)
            team.append(name)
        else:
            # Line is a team member without a position
            team.append(line)

    return Rotation(timer=timer, positions=positions, team=team)


def format_rotation(rotation: Rotation) -> str:
    """Format a Rotation object back to the rotation file format string."""
    lines = [str(rotation.timer)]

    # Add positions with assigned team members
    for i, position in enumerate(rotation.positions):
        if i < len(rotation.team):
            lines.append(f"{position}: {rotation.team[i]}")

    # Add remaining team members without positions
    for i in range(len(rotation.positions), len(rotation.team)):
        lines.append(rotation.team[i])

    # Return without trailing newline to match original format
    return "\n".join(lines)


def parse_json_to_rotation(json_content: str) -> Rotation:
    """Parse JSON string to a Rotation object."""
    try:
        data = json.loads(json_content)
        timer = Timer(
            remaining=parse_time(data["timer"]["remaining"]),
            total=parse_time(data["timer"]["total"]),
        )
        return Rotation(timer=timer, positions=data["positions"], team=data["team"])
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise ValueError(f"Invalid JSON format: {e}")


def main(content: str, format_output: bool = False) -> str:
    """Main function to parse rotation file content or format a rotation object.

    Args:
        content: The rotation file content or JSON string (if format_output is True)
        format_output: If True, parse JSON and output formatted rotation file,
                       otherwise parse rotation file and output JSON

    Returns:
        Formatted output as string (JSON or rotation file format)
    """
    if format_output:
        # Parse JSON to Rotation and format it
        rotation = parse_json_to_rotation(content)
        return format_rotation(rotation)
    else:
        # Parse rotation file to JSON
        rotation = parse_rotation_file(content)
        return json.dumps(rotation.to_dict(), indent=2)


if __name__ == "__main__":
    # Read from stdin
    content = sys.stdin.read()

    # Check if format mode is requested
    format_output = len(sys.argv) > 1 and sys.argv[1] == "format"

    # Run main function
    output = main(content, format_output)

    # Output to stdout (JSON mode adds its own newline, format mode doesn't)
    if format_output:
        # Print without trailing newline
        sys.stdout.write(output)
    else:
        print(output)

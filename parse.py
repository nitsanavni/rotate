#!/usr/bin/env python
import sys
import json
import re
from datetime import time, datetime
from typing import List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Timer:
    elapsed: time
    total: time
    
    def __str__(self) -> str:
        return f"{time_to_str(self.elapsed)} / {time_to_str(self.total)}"


@dataclass
class Rotation:
    timer: Timer
    roles: dict[str, str] = field(default_factory=dict)
    team: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert Rotation object to dictionary for JSON serialization."""
        result = asdict(self)
        # Convert time objects to string format
        result["timer"]["elapsed"] = time_to_str(self.timer.elapsed)
        result["timer"]["total"] = time_to_str(self.timer.total)
        return result


def parse_time(time_str: str) -> time:
    """Parse a time string in format MM:SS to a time object."""
    try:
        minutes, seconds = map(int, time_str.split(':'))
        return time(hour=0, minute=minutes, second=seconds)
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}")


def time_to_str(t: time) -> str:
    """Convert a time object to MM:SS format."""
    return f"{t.minute}:{t.second:02d}"


def parse_timer_line(line: str) -> Timer:
    """Parse the timer line format 'elapsed / total'."""
    match = re.match(r'(\d+:\d+)\s*/\s*(\d+:\d+)', line)
    if not match:
        raise ValueError(f"Invalid timer format: {line}")
    
    elapsed_str, total_str = match.groups()
    elapsed = parse_time(elapsed_str)
    total = parse_time(total_str)
    return Timer(elapsed=elapsed, total=total)


def parse_rotation_file(content: str) -> Rotation:
    """Parse the rotation file content into a Rotation object."""
    lines = content.strip().split('\n')
    
    if not lines:
        raise ValueError("Empty rotation file")
    
    # Parse timer line (first line)
    timer = parse_timer_line(lines[0])
    
    roles = {}
    team = []
    
    # Parse roles and team members
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
            
        # Check if line defines a role
        role_match = re.match(r'(\w+):\s*(.+)', line)
        if role_match:
            role, name = role_match.groups()
            roles[role] = name
        else:
            # Line is a team member without a role
            team.append(line)
    
    return Rotation(timer=timer, roles=roles, team=team)


def main(content: str) -> Rotation:
    """Main function to parse rotation file content."""
    return parse_rotation_file(content)


if __name__ == "__main__":
    # Read from stdin
    content = sys.stdin.read()
    
    # Parse and convert to JSON
    rotation = main(content)
    
    # Output as JSON
    print(json.dumps(rotation.to_dict(), indent=2))
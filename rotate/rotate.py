#!/usr/bin/env python
import sys
from rotate.parse import parse_rotation_file, format_rotation, Rotation


def rotate_team(rotation: Rotation) -> Rotation:
    """Rotate the team members, moving each one position in the list.

    The first team member becomes the last, all others move one position up.
    """
    if not rotation.team:
        return rotation

    # Create a new team list with members rotated
    new_team = rotation.team[1:] + [rotation.team[0]]

    # Create and return a new Rotation with the rotated team
    return Rotation(timer=rotation.timer, positions=rotation.positions, team=new_team)


def main():
    """Read rotation from stdin, rotate the team, and output to stdout."""
    # Read rotation content from stdin
    content = sys.stdin.read()

    # Parse the rotation file
    rotation = parse_rotation_file(content)

    # Rotate the team
    rotated = rotate_team(rotation)

    # Format the rotated rotation and output
    output = format_rotation(rotated)

    # Print without trailing newline to match original format
    sys.stdout.write(output)


if __name__ == "__main__":
    main()

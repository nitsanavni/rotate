#!/usr/bin/env python
import sys
import os
import subprocess
from pathlib import Path


def main():
    """Main entry point for the rotate CLI tool."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == "start":
        start_timer()
    elif command == "init":
        init_rotation()
    elif command == "pause":
        send_command("pause")
    elif command == "resume":
        send_command("resume")
    elif command == "stop":
        send_command("stop")
    elif command == "help":
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()


def print_usage():
    """Print usage information."""
    print("Usage: rotate <command> [options]")
    print("\nCommands:")
    print("  init     Initialize a new rotation file")
    print("  start    Start the timer daemon")
    print("  pause    Pause the running timer")
    print("  resume   Resume a paused timer")
    print("  stop     Stop the running timer daemon")
    print("  help     Show this help message")


def init_rotation():
    """Initialize a new rotation file from template."""
    if len(sys.argv) < 3:
        print("Usage: rotate init <file_path> [team_member1 team_member2 ...]")
        return

    output_path = sys.argv[2]

    # Check if file already exists
    if os.path.exists(output_path):
        print(f"Error: File already exists: {output_path}")
        return

    # Get team members from arguments or use defaults
    team_members = (
        sys.argv[3:]
        if len(sys.argv) > 3
        else ["Alice", "Bob", "Charlie", "Diana", "Eva"]
    )

    # Create rotation file
    with open(output_path, "w") as f:
        f.write("5:00 / 5:00\n")
        if len(team_members) > 0:
            f.write(f"Typing: {team_members[0]}\n")
        if len(team_members) > 1:
            f.write(f"Talking: {team_members[1]}\n")
        if len(team_members) > 2:
            f.write(f"Next: {team_members[2]}\n")

        # Add remaining team members
        for member in team_members[3:]:
            f.write(f"{member}\n")

    print(f"Rotation file created: {output_path}")


def get_ipc_file_path(rotation_file_path: str) -> str:
    """Generate the IPC file path based on the rotation file path."""
    return f"{rotation_file_path}.ipc"


def send_command(command: str):
    """Send a command to the running daemon via IPC file."""
    if len(sys.argv) < 3:
        print(f"Usage: rotate {command} <rotation_file_path>")
        return

    file_path = sys.argv[2]

    # Check if rotation file exists
    if not os.path.exists(file_path):
        print(f"Error: Rotation file not found: {file_path}")
        return

    # Create IPC file
    ipc_file_path = get_ipc_file_path(file_path)
    with open(ipc_file_path, "w") as f:
        f.write(command)

    print(f"Sent '{command}' command for {file_path}")


def start_timer():
    """Start the timer daemon."""
    if len(sys.argv) < 3:
        print("Usage: rotate start <rotation_file_path> [update_interval]")
        return

    file_path = sys.argv[2]

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: Rotation file not found: {file_path}")
        return

    # Get update interval if provided
    update_interval = sys.argv[3] if len(sys.argv) > 3 else "1"

    # Get the path to daemon.py relative to this script
    daemon_script = Path(__file__).parent / "daemon.py"

    try:
        # Start daemon process in background
        subprocess.Popen(
            [sys.executable, str(daemon_script), file_path, update_interval],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"Timer daemon started for {file_path}")
    except Exception as e:
        print(f"Error starting daemon: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)

#!/usr/bin/env python
import sys
import os
import subprocess
from rotate.hooks import ensure_hooks_directory_exists
from rotate.parse import parse_rotation_file, format_rotation
from rotate.rotate import rotate_team


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
    elif command == "rotate":
        rotate_team_members()
    elif command == "help":
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()


def print_usage():
    """Print usage information."""
    print("Usage: rotate <command> [options]")
    print("\nCommands:")
    print("  init     Initialize a new rotation file (default: '.rotate/rotation')")
    print("  start    Start the timer daemon (default file: '.rotate/rotation')")
    print("  pause    Pause the running timer (default file: '.rotate/rotation')")
    print("  resume   Resume a paused timer (default file: '.rotate/rotation')")
    print("  stop     Stop the running timer daemon (default file: '.rotate/rotation')")
    print("  rotate   Rotate team members [count] [file] (default file: '.rotate/rotation')")
    print("  help     Show this help message")
    print("\nHooks:")
    print("  Place executable scripts in the .rotate/hooks/ directory.")
    print("  The 'expire' hook runs when timer expires or the daemon stops.")


def init_rotation():
    """Initialize a new rotation file from template."""
    from rotate.hooks import get_default_rotation_file_path, ensure_rotate_directory_exists
    
    # Ensure .rotate directory exists
    ensure_rotate_directory_exists()
    
    # Default to .rotate/rotation
    output_path = get_default_rotation_file_path()
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]

    team_members_start = 3
    if len(sys.argv) < 3:
        team_members_start = 2

    # Check if file already exists
    if os.path.exists(output_path):
        print(f"Error: File already exists: {output_path}")
        return

    # Get team members from arguments or use defaults
    team_members = (
        sys.argv[team_members_start:]
        if len(sys.argv) > team_members_start
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

    # Create hooks directory
    hooks_dir = ensure_hooks_directory_exists()
    print(f"Hooks directory created: {hooks_dir}")


def get_ipc_file_path(rotation_file_path: str) -> str:
    """Generate the IPC file path based on the rotation file path."""
    return f"{rotation_file_path}.ipc"


def send_command(command: str):
    """Send a command to the running daemon via IPC file."""
    from rotate.hooks import get_default_rotation_file_path
    
    file_path = get_default_rotation_file_path()
    if len(sys.argv) >= 3:
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
    from rotate.hooks import get_default_rotation_file_path
    
    file_path = get_default_rotation_file_path()
    if len(sys.argv) >= 3:
        file_path = sys.argv[2]

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: Rotation file not found: {file_path}")
        return

    # Get update interval if provided
    update_interval = sys.argv[3] if len(sys.argv) > 3 else "1"

    try:
        # Start daemon process in background
        subprocess.Popen(
            [sys.executable, "-m", "rotate.daemon", file_path, update_interval],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"Timer daemon started for {file_path}")
    except Exception as e:
        print(f"Error starting daemon: {e}")


def rotate_team_members():
    """Rotate team members in the rotation file."""
    from rotate.hooks import get_default_rotation_file_path
    
    # Determine rotation file path
    args_idx = 2
    file_path = get_default_rotation_file_path()
    
    # Check if next arg is a number or a file path
    if len(sys.argv) >= 3:
        if sys.argv[2].isdigit():
            count = int(sys.argv[2])
            args_idx = 3  # File path might be at position 3
        else:
            count = 1
            file_path = sys.argv[2]
    else:
        count = 1
    
    # Check if there's a file path after count
    if len(sys.argv) > args_idx:
        file_path = sys.argv[args_idx]

    # Check if rotation file exists
    if not os.path.exists(file_path):
        print(f"Error: Rotation file not found: {file_path}")
        return

    try:
        # Read current rotation
        with open(file_path, "r") as f:
            content = f.read()
        
        # Parse the rotation file
        rotation = parse_rotation_file(content)
        
        # Rotate the team multiple times if specified
        rotated = rotation
        for _ in range(count):
            rotated = rotate_team(rotated)
        
        # Format the rotated rotation
        output = format_rotation(rotated)
        
        # Write back to file
        with open(file_path, "w") as f:
            f.write(output)
            
        times = "time" if count == 1 else "times"
        print(f"Team rotated {count} {times} in {file_path}")
    except Exception as e:
        print(f"Error rotating team: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)

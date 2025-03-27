#!/usr/bin/env python
import sys
import os
import subprocess
from rotate.hooks import ensure_hooks_directory_exists
from rotate.rotate import rotate_team
from rotate.rotation import (
    read_rotation_file,
    write_rotation_file,
    create_rotation_file,
)
from rotate.ipc import write_command


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
    elif command == "cat":
        cat_rotation_file()
    elif command == "open" or command == "edit":
        open_rotation_file()
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
    print(
        "  rotate   Rotate team members [count] [file] (default file: '.rotate/rotation')"
    )
    print("  cat      Display the content of the rotation file")
    print("  open     Open the rotation file in your default editor (also: edit)")
    print("  help     Show this help message")
    print("\nHooks:")
    print("  Place executable scripts in the .rotate/hooks/ directory.")
    print("  The 'expire' hook runs when timer expires or the daemon stops.")


def init_rotation():
    """Initialize a new rotation file from template."""
    from rotate.hooks import (
        get_default_rotation_file_path,
        ensure_rotate_directory_exists,
    )

    # Ensure .rotate directory exists
    ensure_rotate_directory_exists()

    # Default to .rotate/rotation
    output_path = get_default_rotation_file_path()
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]

    team_members_start = 3
    if len(sys.argv) < 3:
        team_members_start = 2

    # Get team members from arguments or use defaults
    team_members = (
        sys.argv[team_members_start:]
        if len(sys.argv) > team_members_start
        else ["Alice", "Bob", "Charlie", "Diana", "Eva"]
    )

    try:
        # Create rotation file
        create_rotation_file(output_path, team_members)
        print(f"Rotation file created: {output_path}")
    except FileExistsError:
        print(f"Error: File already exists: {output_path}")
        return

    # Create hooks directory
    hooks_dir = ensure_hooks_directory_exists()
    print(f"Hooks directory created: {hooks_dir}")


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
    write_command(file_path, command)

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

    try:
        # Read current rotation
        rotation = read_rotation_file(file_path)

        # Rotate the team multiple times if specified
        rotated = rotation
        for _ in range(count):
            rotated = rotate_team(rotated)

        # Write back to file
        write_rotation_file(file_path, rotated)

        times = "time" if count == 1 else "times"
        print(f"Team rotated {count} {times} in {file_path}")
    except FileNotFoundError:
        print(f"Error: Rotation file not found: {file_path}")
    except Exception as e:
        print(f"Error rotating team: {e}")


def cat_rotation_file():
    """Display the content of the rotation file to stdout."""
    from rotate.hooks import get_default_rotation_file_path

    # Determine rotation file path
    file_path = get_default_rotation_file_path()
    if len(sys.argv) >= 3:
        file_path = sys.argv[2]

    try:
        # Read and print file content
        with open(file_path, "r") as f:
            content = f.read()

        print(content, end="")
    except FileNotFoundError:
        print(f"Error: Rotation file not found: {file_path}")
    except Exception as e:
        print(f"Error reading rotation file: {e}")


def open_rotation_file():
    """Open the rotation file in the default editor."""
    from rotate.hooks import get_default_rotation_file_path

    # Determine rotation file path
    file_path = get_default_rotation_file_path()
    if len(sys.argv) >= 3:
        file_path = sys.argv[2]

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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)

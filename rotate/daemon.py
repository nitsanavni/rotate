#!/usr/bin/env python
import sys
import time
import signal
import os
from datetime import datetime, timedelta
from rotate.parse import (
    parse_rotation_file,
    format_rotation,
    Timer,
    Rotation,
    time_to_str,
)
from rotate.rotate import rotate_team
from rotate.hooks import execute_hooks


def time_to_timedelta(t) -> timedelta:
    """Convert time object to timedelta."""
    return timedelta(minutes=t.minute, seconds=t.second)


def timedelta_to_time(td: timedelta):
    """Convert timedelta to time object."""
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return datetime.strptime(f"{minutes}:{seconds:02d}", "%M:%S").time()


def update_rotation_file(file_path: str, rotation: Rotation):
    """Update the rotation file with the current rotation state."""
    formatted = format_rotation(rotation)
    with open(file_path, "w") as f:
        f.write(formatted)
    print(f"File updated: {file_path}")


def get_ipc_file_path(rotation_file_path: str) -> str:
    """Generate the IPC file path based on the rotation file path."""
    return f"{rotation_file_path}.ipc"


def read_ipc_commands(ipc_file_path: str):
    """Read commands from the IPC file and then delete it."""
    if not os.path.exists(ipc_file_path):
        return None

    try:
        with open(ipc_file_path, "r") as f:
            command = f.read().strip()

        # Delete the file after reading
        os.unlink(ipc_file_path)
        return command
    except Exception as e:
        print(f"Error reading IPC file: {e}")
        return None


def start_daemon(file_path: str, update_interval: int = 1):
    """Start the daemon process to track remaining time and update the rotation file.

    Args:
        file_path: Path to the rotation file
        update_interval: Time in seconds between updates
    """
    print(f"Starting daemon for {file_path}...")

    def signal_handler(sig, frame):
        print("\nDaemon stopping...")
        # Trigger exit hooks before terminating
        print("Triggering expire hook before exit...")
        execute_hooks("expire", file_path)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # IPC file path
    ipc_file_path = get_ipc_file_path(file_path)

    # Clean up any existing IPC file
    if os.path.exists(ipc_file_path):
        os.unlink(ipc_file_path)

    # Read the initial rotation file
    with open(file_path, "r") as f:
        content = f.read()

    print(f"Initial content: {content.strip()}")

    # Parse rotation
    rotation = parse_rotation_file(content)

    # Get time values
    total_seconds = time_to_timedelta(rotation.timer.total).total_seconds()
    remaining_seconds = time_to_timedelta(rotation.timer.remaining).total_seconds()

    # Start time
    start_timestamp = datetime.now()
    print(f"Start time: {start_timestamp}")
    print(f"Initial values: Remaining: {remaining_seconds}s, Total: {total_seconds}s")

    # Update interval in seconds
    update_interval = int(update_interval)
    print(f"Update interval: {update_interval} seconds")

    # Flag to indicate if timer is paused
    is_paused = False
    pause_timestamp = None

    while True:
        try:
            # Check for IPC commands
            command = read_ipc_commands(ipc_file_path)
            if command:
                print(f"Received command: {command}")

                if command == "pause":
                    if not is_paused:
                        is_paused = True
                        pause_timestamp = datetime.now()
                        print("Timer paused")
                elif command == "resume":
                    if is_paused and pause_timestamp is not None:
                        # Adjust start timestamp by pause duration
                        pause_duration = (
                            datetime.now() - pause_timestamp
                        ).total_seconds()
                        start_timestamp = start_timestamp + timedelta(
                            seconds=pause_duration
                        )
                        is_paused = False
                        print(f"Timer resumed (paused for {pause_duration:.1f}s)")
                elif command == "stop":
                    print("Stopping daemon...")
                    # Stop without triggering the expire hook
                    break

            # Skip time updates if paused
            if is_paused:
                time.sleep(update_interval)
                continue

            # Calculate time since start
            now = datetime.now()
            seconds_since_start = (now - start_timestamp).total_seconds()

            # Update remaining time
            new_remaining_seconds = remaining_seconds - seconds_since_start

            # Ensure we don't go below zero
            if new_remaining_seconds < 0:
                new_remaining_seconds = 0

            # Calculate remaining time in minutes:seconds format
            remaining_time = timedelta_to_time(timedelta(seconds=new_remaining_seconds))

            # Create updated rotation with new timer values
            updated_timer = Timer(remaining=remaining_time, total=rotation.timer.total)
            updated_rotation = Rotation(
                timer=updated_timer, positions=rotation.positions, team=rotation.team
            )

            # Update the file
            update_rotation_file(file_path, updated_rotation)

            # Print status
            elapsed = total_seconds - new_remaining_seconds
            print(
                f"Updated: Remaining: {time_to_str(remaining_time)}, "
                f"Elapsed: {int(elapsed // 60)}:{int(elapsed % 60):02d}"
            )

            # Check if timer has expired
            if new_remaining_seconds <= 0:
                print("\nTimer expired! Triggering rotation...")

                # Trigger the expire hook before rotating
                print("Triggering expire hook...")
                execute_hooks("expire", file_path)

                # Rotate the team
                updated_rotation = rotate_team(updated_rotation)

                # Reset the turn timer to total
                updated_rotation.timer.remaining = updated_rotation.timer.total

                # Update the file with the rotated team
                update_rotation_file(file_path, updated_rotation)

                print("Rotation complete. Use 'rotate start' to start the next timer.")
                break

            # Sleep for the update interval
            time.sleep(update_interval)

        except FileNotFoundError:
            print(f"\nError: Rotation file not found: {file_path}")
            break
        except Exception as e:
            print(f"\nError in daemon: {e}")
            import traceback

            traceback.print_exc()
            break


def main():
    """Main function for the daemon script."""
    # Simple argument handling
    if len(sys.argv) < 2:
        print("Usage: python daemon.py <rotation_file_path> [update_interval]")
        sys.exit(1)

    file_path = sys.argv[1]

    # Optional update interval
    update_interval = 1
    if len(sys.argv) > 2:
        try:
            update_interval = int(sys.argv[2])
        except ValueError:
            print(f"Invalid update interval: {sys.argv[2]}. Using default (1 second).")

    start_daemon(file_path, update_interval)


if __name__ == "__main__":
    main()

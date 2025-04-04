#!/usr/bin/env python
import sys
import time
import signal
from datetime import datetime, timedelta
from rotate.parse import (
    Timer,
    Rotation,
    time_to_str,
)
from rotate.rotation import read_rotation_file, write_rotation_file
from rotate.ipc import read_command, cleanup_ipc_file
from rotate.rotate import rotate_team
from rotate.hooks import execute_hooks


def time_to_timedelta(t) -> timedelta:
    return timedelta(minutes=t.minute, seconds=t.second)


def timedelta_to_time(td: timedelta):
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return datetime.strptime(f"{minutes}:{seconds:02d}", "%M:%S").time()


def update_rotation_file(file_path: str, rotation: Rotation):
    write_rotation_file(file_path, rotation)
    print(f"File updated: {file_path}")


def setup_signal_handlers(file_path: str) -> None:
    def signal_handler(sig, frame):
        print("\nDaemon stopping...")
        print("Triggering expire hook before exit...")
        execute_hooks("expire", file_path)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def load_initial_rotation(file_path: str) -> tuple[Rotation, float, float]:
    try:
        rotation = read_rotation_file(file_path)
        print(f"Initial content loaded from: {file_path}")

        total_seconds = time_to_timedelta(rotation.timer.total).total_seconds()
        remaining_seconds = time_to_timedelta(rotation.timer.remaining).total_seconds()
        return rotation, total_seconds, remaining_seconds
    except Exception as e:
        print(f"Error reading rotation file: {e}")
        raise


def handle_command(
    command: str,
    is_paused: bool,
    pause_timestamp: datetime | None,
    start_timestamp: datetime,
) -> tuple[bool, datetime | None, datetime, bool]:
    should_stop = False

    if command == "pause":
        if not is_paused:
            is_paused = True
            pause_timestamp = datetime.now()
            print("Timer paused")
    elif command == "resume":
        if is_paused and pause_timestamp is not None:
            pause_duration = (datetime.now() - pause_timestamp).total_seconds()
            start_timestamp = start_timestamp + timedelta(seconds=pause_duration)
            is_paused = False
            print(f"Timer resumed (paused for {pause_duration:.1f}s)")
    elif command == "stop":
        print("Stopping daemon...")
        should_stop = True

    return is_paused, pause_timestamp, start_timestamp, should_stop


def update_timer(
    file_path: str,
    rotation: Rotation,
    remaining_seconds: float,
    total_seconds: float,
    start_timestamp: datetime,
) -> tuple[Rotation, float, bool]:
    now = datetime.now()
    seconds_since_start = (now - start_timestamp).total_seconds()
    new_remaining_seconds = remaining_seconds - seconds_since_start

    if new_remaining_seconds < 0:
        new_remaining_seconds = 0

    remaining_time = timedelta_to_time(timedelta(seconds=new_remaining_seconds))
    updated_timer = Timer(remaining=remaining_time, total=rotation.timer.total)
    updated_rotation = Rotation(
        timer=updated_timer, positions=rotation.positions, team=rotation.team
    )

    update_rotation_file(file_path, updated_rotation)

    elapsed = total_seconds - new_remaining_seconds
    print(
        f"Updated: Remaining: {time_to_str(remaining_time)}, "
        f"Elapsed: {int(elapsed // 60)}:{int(elapsed % 60):02d}"
    )

    timer_expired = new_remaining_seconds <= 0
    return updated_rotation, new_remaining_seconds, timer_expired


def handle_timer_expiration(file_path: str, updated_rotation: Rotation) -> Rotation:
    print("\nTimer expired! Triggering rotation...")
    print("Triggering expire hook...")
    execute_hooks("expire", file_path)

    updated_rotation = rotate_team(updated_rotation)
    updated_rotation.timer.remaining = updated_rotation.timer.total

    update_rotation_file(file_path, updated_rotation)
    print("Rotation complete. Use 'rotate start' to start the next timer.")

    return updated_rotation


def start_daemon(file_path: str, update_interval: int = 1):
    print(f"Starting daemon for {file_path}...")

    setup_signal_handlers(file_path)
    cleanup_ipc_file(file_path)

    try:
        rotation, total_seconds, remaining_seconds = load_initial_rotation(file_path)
    except Exception:
        return

    start_timestamp = datetime.now()
    print(f"Start time: {start_timestamp}")
    print(f"Initial values: Remaining: {remaining_seconds}s, Total: {total_seconds}s")

    update_interval = int(update_interval)
    print(f"Update interval: {update_interval} seconds")

    is_paused = False
    pause_timestamp = None

    while True:
        try:
            command = read_command(file_path)
            if command:
                print(f"Received command: {command}")
                is_paused, pause_timestamp, start_timestamp, should_stop = (
                    handle_command(command, is_paused, pause_timestamp, start_timestamp)
                )
                if should_stop:
                    break

            if is_paused:
                time.sleep(update_interval)
                continue

            updated_rotation, new_remaining_seconds, timer_expired = update_timer(
                file_path, rotation, remaining_seconds, total_seconds, start_timestamp
            )

            if timer_expired:
                updated_rotation = handle_timer_expiration(file_path, updated_rotation)
                break

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

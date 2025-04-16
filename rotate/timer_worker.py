"""
timer_worker.py
Runs the rotation timer loop as a standalone process.
Invoked by the CLI as a subprocess for non-blocking UX.
"""
import sys
import time
from rotation import RotationState, run_expiry_hooks, ROTATION_FILE

# For simplicity, positions and duration are hardcoded here, but ideally should be passed in or read from config/rotation file
POSITIONS = ["Talking", "Typing", "Next"]
DURATION_SECONDS = 4 * 60  # Default 4:00


def main():
    # Read current state
    state = RotationState.read_from_file(ROTATION_FILE, positions=POSITIONS, duration_seconds=DURATION_SECONDS)
    while state.current_time > 0:
        time.sleep(1)
        state.current_time -= 1
        state.write_to_file()
        # Optionally: check for file modification to exit early (manual edit)
        # (not implemented here)
    # Timer expired
    state.rotate()
    state.write_to_file()
    run_expiry_hooks()

if __name__ == "__main__":
    main()

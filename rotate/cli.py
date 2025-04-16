"""
CLI argument parsing and command dispatch for the rotate tool.
"""
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        prog="rotate",
        description="A CLI tool for file rotation and session management."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Define subcommands (stubs)
    subparsers.add_parser("init", help="Initialize a new rotation session.")
    subparsers.add_parser("start", help="Start the rotation timer.")
    subparsers.add_parser("stop", help="Stop the rotation timer.")
    subparsers.add_parser("rotate", help="Manually rotate to the next item.")
    subparsers.add_parser("randomize", help="Randomize the rotation order.")
    subparsers.add_parser("watch", help="Watch for changes and auto-rotate.")
    subparsers.add_parser("open", help="Open the current item.")

    args = parser.parse_args()

    # Command dispatch (stub)
    if args.command == "init":
        import os
        from rotation import RotationState, ROTATION_FILE, HOOKS_DIR
        import shutil

        # Parse non-interactive flag
        import sys
        non_interactive = "-y" in sys.argv

        if non_interactive:
            # Use defaults
            people = ["Nitsan", "Michael", "Bob", "Jay", "Julie"]
            positions = ["Talking", "Typing", "Next"]
            duration_seconds = 4 * 60
        else:
            # Interactive prompts
            print("Enter names (comma-separated or one per line, blank to finish):")
            names = []
            while True:
                line = input()
                if not line.strip():
                    break
                if "," in line:
                    names += [n.strip() for n in line.split(",") if n.strip()]
                    break
                else:
                    names.append(line.strip())
            people = names if names else ["Nitsan", "Michael", "Bob", "Jay", "Julie"]
            pos_in = input("Enter positions (comma-separated, default: Talking,Typing,Next): ").strip()
            positions = [p.strip() for p in pos_in.split(",")] if pos_in else ["Talking", "Typing", "Next"]
            dur_in = input("Enter turn duration in minutes (default 4): ").strip()
            try:
                duration_seconds = int(float(dur_in) * 60) if dur_in else 4 * 60
            except Exception:
                duration_seconds = 4 * 60

        # Create rotation state and write file
        state = RotationState(positions, people, duration_seconds)
        state.write_to_file()
        print(f"Rotation session initialized with {len(people)} people, positions: {positions}, duration: {duration_seconds//60}:{duration_seconds%60:02d}")

        # Create default hook if not present
        os.makedirs(HOOKS_DIR, exist_ok=True)
        hook_path = os.path.join(HOOKS_DIR, "expire-open.sh")
        if not os.path.exists(hook_path):
            with open(hook_path, "w") as f:
                f.write("#!/bin/sh\nrotate open\n")
            os.chmod(hook_path, 0o755)
            print(f"Default hook created at {hook_path}")

    elif args.command == "start":
        import subprocess
        import os
        # Launch timer_worker.py as a detached subprocess
        script = os.path.join(os.path.dirname(__file__), "timer_worker.py")
        try:
            subprocess.Popen([
                sys.executable, script
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            print("Timer started in background.")
        except Exception as e:
            print(f"Failed to start timer: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "stop":
        print("[STUB] Stopping rotation timer...")
    elif args.command == "rotate":
        print("[STUB] Rotating to next item...")
    elif args.command == "randomize":
        print("[STUB] Randomizing rotation order...")
    elif args.command == "watch":
        print("[STUB] Watching for changes...")
    elif args.command == "open":
        print("[STUB] Opening current item...")
    else:
        parser.print_help()
        sys.exit(1)

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
        print("[STUB] Initializing rotation session...")
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

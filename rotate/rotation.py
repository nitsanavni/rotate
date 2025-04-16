"""
rotation.py
Core logic for managing the rotation state, timer countdown, and file I/O for `.rotate/rotation`.
"""
import os
import time
import threading
from typing import List, Dict, Optional

ROTATE_DIR = ".rotate"
ROTATION_FILE = os.path.join(ROTATE_DIR, "rotation")
HOOKS_DIR = os.path.join(ROTATE_DIR, "hooks")

class RotationState:
    def __init__(self, positions: List[str], people: List[str], duration_seconds: int, current_time: Optional[int] = None):
        self.positions = positions  # e.g. ["Talking", "Typing", "Next"]
        self.people = people        # e.g. ["Nitsan", "Michael", "Bob", "Jay", "Julie"]
        self.duration_seconds = duration_seconds
        self.current_time = current_time if current_time is not None else duration_seconds

    def rotate(self):
        # Move everyone up, first person goes to end
        if self.people:
            self.people = self.people[1:] + self.people[:1]
        self.current_time = self.duration_seconds

    def randomize(self):
        import random
        random.shuffle(self.people)
        self.current_time = self.duration_seconds

    def to_lines(self) -> List[str]:
        # Format: "3:42 / 4:00"\n"Talking: Nitsan"\n"Typing: Michael"\n"Next: Bob"\n"Jay"\n"Julie"
        cur = f"{self.current_time//60}:{self.current_time%60:02d} / {self.duration_seconds//60}:{self.duration_seconds%60:02d}"
        lines = [cur]
        for i, pos in enumerate(self.positions):
            name = self.people[i] if i < len(self.people) else ""
            lines.append(f"{pos}: {name}")
        for name in self.people[len(self.positions):]:
            lines.append(name)
        return lines

    @staticmethod
    def from_lines(lines: List[str], positions: List[str], duration_seconds: int) -> 'RotationState':
        # Parse from the rotation file
        if not lines:
            raise ValueError("Rotation file is empty")
        time_part = lines[0].split("/")
        current_time = duration_seconds
        if len(time_part) == 2:
            left = time_part[0].strip()
            if ":" in left:
                m, s = map(int, left.split(":"))
                current_time = m * 60 + s
        people = []
        for line in lines[1:]:
            if ":" in line:
                _, name = line.split(":", 1)
                people.append(name.strip())
            else:
                people.append(line.strip())
        return RotationState(positions, people, duration_seconds, current_time)

    def write_to_file(self, filename=ROTATION_FILE):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            for line in self.to_lines():
                f.write(line + "\n")

    @staticmethod
    def read_from_file(filename=ROTATION_FILE, positions=None, duration_seconds=None):
        with open(filename) as f:
            lines = [l.rstrip("\n") for l in f]
        if positions is None or duration_seconds is None:
            raise ValueError("Positions and duration_seconds must be provided")
        return RotationState.from_lines(lines, positions, duration_seconds)

class RotationTimer:
    def __init__(self, state: RotationState, on_expire=None):
        self.state = state
        self.on_expire = on_expire
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()

    def _run(self):
        while self._running and self.state.current_time > 0:
            time.sleep(1)
            self.state.current_time -= 1
            self.state.write_to_file()
        if self._running and self.state.current_time <= 0:
            # Timer expired
            self.state.rotate()
            self.state.write_to_file()
            if self.on_expire:
                self.on_expire()

# Example hook runner (to be used by cli.py):
def run_expiry_hooks():
    if not os.path.isdir(HOOKS_DIR):
        return
    for fname in os.listdir(HOOKS_DIR):
        if fname.startswith("expire") and os.access(os.path.join(HOOKS_DIR, fname), os.X_OK):
            path = os.path.join(HOOKS_DIR, fname)
            log_path = path + ".log"
            import subprocess
            with open(log_path, "w") as logf:
                subprocess.Popen([path], stdout=logf, stderr=logf)

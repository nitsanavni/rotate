# Mob Rotation Timer: `rotate`

## Overview

`rotate` is a CLI tool designed to manage mob programming sessions by handling timed rotations for team members. It supports configurable turn durations, dynamic position assignments, and integrates with hooks for custom alerts. The tool uses a local file (`.rotate/rotation`) to persist its state and allows users to modify session details interactively.

## File Structure

- **Rotation File:**

  - Location: `.rotate/rotation`
  - Format Example:
    ```
    3:42 / 4:00
    Talking: Nitsan
    Typing: Michael
    Next: Bob
    Jay
    Julie
    ```
  - The first line shows the current countdown and the total turn duration.
  - Lines with a label (e.g., "Talking:") indicate positions assigned to specific people.
  - Additional names without labels follow after the positions.

- **Hooks Directory:**
  - Location: `.rotate/hooks`
  - Example Hook:
    - File: `expire-open.sh`
    - Contents:
      ```shell
      #!/bin/sh
      rotate open
      ```
    - Purpose: Executes upon timer expiry to open the rotation file in the default editor.

## CLI Commands

### Initialization

- **`rotate init`**
  - **Interactive Mode:**
    - Prompts for:
      - People names (input one-by-one or as a comma-separated list).
      - Turn duration (default: 4:00).
      - Positions (default: "Talking", "Typing", "Next").
  - **Non-Interactive Mode:**
    - Command: `rotate init -y`
    - Uses default template values:
      - Turn Duration: 4:00 (displayed as `4:00 / 4:00`).
      - Positions: "Talking", "Typing", "Next".
      - People Names: A preset sample list (e.g., "Nitsan, Michael, Bob, Jay, Julie") or empty by choice.
  - **Default Hook Setup:**
    - Creates the default hook at `.rotate/hooks/expire-open.sh` with the script:
      ```shell
      #!/bin/sh
      rotate open
      ```

### Timer Control

- **`rotate start`**

  - Starts the countdown timer in the background.
  - The timer updates the rotation file in real time (with one-second precision) but does not print updates to the terminal.

- **`rotate stop`**
  - Stops the countdown and resets the timer to the full turn duration (e.g., 4:00 / 4:00).

### Rotation & Randomization

- **`rotate rotate`**

  - Manually triggers a rotation.
  - Automatically rotates when the timer expires.
  - Rotation logic: each person moves one position up in the list, with the first person moving to the bottom.

- **`rotate randomize`**
  - Shuffles only the names of the people.
  - The positions and the timer remain unchanged.

### Display and Editing

- **`rotate watch`**
  - Functions like `watch -n 0.3 -t cat .rotate/rotation`.
  - Continuously displays the current state of the rotation file in real time.
- **`rotate open`**
  - Opens the rotation file in the system’s default editor (respects the `$EDITOR` environment variable).

## Hooks & Expiry Behavior

- **Timer Expiry:**
  - When the countdown reaches zero:
    - The rotation is triggered automatically.
    - The timer is reset.
    - All executable hook files in `.rotate/hooks` with names starting with `expire` are executed concurrently.
    - Each hook’s output is logged to a corresponding file in the hooks directory (e.g., `.rotate/hooks/expire-open.sh.log`).

## User Interaction & Dynamic Updates

- **Direct File Editing:**
  - Users can directly edit the rotation file to update names and positions.
- **Editing During Active Timer:**
  - If the file is modified while the timer is running, the background countdown and real-time updates should gracefully stop to allow manual intervention.

## Additional Considerations

- **Process Persistence:**
  - The tool does not support resuming timer state across CLI sessions or system restarts.
- **Mob Session:**
  - Designed for a single mob session at a time.
- **Timer Precision:**
  - The timer operates with one-second precision; no sub-second adjustments are implemented.

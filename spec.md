Below is a detailed specification and architecture overview for the mob timer CLI app.

---

# Mob Timer CLI App Specification and Architecture

This document outlines the functional requirements, data formats, and system architecture for the mob programming rotation manager. The goal is to have a CLI tool called `rotate` that is simple to use, cross-platform, and extensible with hooks and configurable state stored in files.

---

## 1. Functional Requirements

### 1.1 Core Features

- **Timer Management:**  
  - Start, pause, resume, and stop a timer that tracks the duration of a mob programming turn.
  - When the timer expires, trigger hooks and rotate team member roles.

- **Rotation Management:**  
  - Maintain an ordered list of team member names.
  - Track specific positions such as **Typing**, **Talking**, and **Next**.
  - Rotate the list so that after a turn expires the roles update:
    - For example, after rotation:
      ```
      4:00 / 4:00
      Typing: Llewellyn
      Talking: Diana
      Next: Susan
      Michael
      Nitsan
      ```

- **File-Based State:**  
  - Use a text-based rotation file to store current timer values, roles, and the team order.
  - Support an easy-to-edit format where one name per line is acceptable.
  - Include additional configuration data (e.g., full turn duration) using a structured format (like TOML).

- **Hooks and Extensibility:**  
  - Allow registering of custom scripts (hooks) under a designated directory (e.g. `.rotate/hooks`).
  - Hooks can be name- or event-specific (for instance, switching display mode when a specific person’s turn starts or ends).

### 1.2 CLI Commands

- **Initialization & Parsing:**
  - `rotate init`  
    Create a new rotation file using a predefined template. This gives users a starting point.
  
  - `rotate parse`  
    Read the rotation file, parse the state, and output a human-readable description (or a structured output) to stdout.

- **Timer Control:**
  - `rotate` or `rotate start`  
    Start the timer for the current turn. This command launches the background process (daemon) that tracks the timer.
  
  - `rotate pause`  
    Pause the timer. The command communicates with the background process to halt time progression.
  
  - `rotate resume`  
    Resume the timer from a paused state.
  
  - `rotate stop`  
    Stop the timer and the background process, persisting the current state.

- **File Interaction:**
  - `rotate open`  
    Open the rotation file in a user-defined editor. This can help everyone visually confirm or modify the rotation.
  
  - `rotate cat`  
    Dump the contents of the rotation file to stdout for quick inspection.

- **Additional (Optional) Commands:**
  - A command to randomize the team order, if desired.
  - A status command to quickly query the current state of the timer and rotation.

---

## 2. Data Formats

### 2.1 Rotation File Format

A simple text format that might look like:

```
1:32 / 4:00
Typing: Nitsan
Talking: Llewellyn
Next: Diana
Susan
Michael
```

- **Timer Line:**  
  The first line shows elapsed time vs. full turn time.
  
- **Role Assignment:**  
  The following lines specify roles. The first few lines might assign roles explicitly (e.g., “Typing”, “Talking”, “Next”), while the remaining lines represent the rest of the ordered team.

- **Extensibility:**  
  Consider using markers or delimiters if additional metadata is needed later.

### 2.2 Configuration File

- Use a TOML or similar format for session configuration (e.g., default turn duration, editor command, etc.).
- Keep it separate from the rotation file to distinguish between dynamic state and session configuration.

### 2.3 Hooks Directory

- **Location:**  
  A directory (e.g., `.rotate/hooks`) where scripts are placed.
- **Naming Convention:**  
  The file name can encode the event (for example, `Llewellyn_start.sh` for when Llewellyn’s turn starts, `Llewellyn_end.sh` for when it ends).

---

## 3. Architecture Overview

### 3.1 High-Level Components

1. **CLI Interface Module:**  
   - **Purpose:**  
     Parses user commands and dispatches them accordingly.
   - **Tools:**  
     Python’s `argparse` or a framework like `click` for a clean command structure.
   - **Responsibilities:**  
     - Launching the timer process (using `rotate start`).
     - Sending control commands (pause, resume, stop) to the background process.

2. **Timer Daemon (Background Process):**  
   - **Purpose:**  
     Manages the countdown for the current turn.
   - **Lifecycle:**  
     - Spawned when `rotate start` is invoked.
     - Runs until the turn expires, is paused, or is stopped.
     - Detaches from the CLI (daemonizes) so that the command exits immediately after launch.
   - **Responsibilities:**  
     - Update the rotation file with the current timer status.
     - Trigger hooks on expiration.
     - Rotate the team order at the end of the turn.
     - Handle pause/resume commands.

3. **State Management Module:**  
   - **Purpose:**  
     Reads and writes the rotation file and configuration file.
   - **Responsibilities:**  
     - Parsing the rotation file into an internal data structure.
     - Serializing state back into the file.
     - Providing a clear interface for other components (like the timer and CLI) to query or update the current state.

4. **Inter-Process Communication (IPC) Module:**  
   - **Purpose:**  
     Allows communication between the CLI commands and the background process.
   - **Approaches:**  
     - **TCP Socket on Localhost:**  
       A simple server–client model using a known port or a port specified in a state file. This approach is cross-platform.
     - **Cross-Platform Abstractions:**  
       Libraries or custom wrappers that use named pipes on Windows and Unix domain sockets on Unix-like systems.
   - **Responsibilities:**  
     - Listening for commands (pause, resume, stop) in the background process.
     - Sending commands from the CLI process to the background process.

5. **Hooks Module:**  
   - **Purpose:**  
     Manage execution of custom hook scripts on timer events.
   - **Responsibilities:**  
     - Detecting which hooks should be triggered based on the current state (e.g., current name, event type).
     - Executing hook scripts in a secure and controlled environment.
     - Handling errors or logging output from hooks.

---

### 3.2 Process Flow

1. **Starting a Timer Turn:**
   - User executes `rotate start` (or just `rotate`).
   - The CLI module launches the timer daemon as a detached background process.
   - The timer daemon:
     - Loads the current state from the rotation file.
     - Begins counting down (using an asynchronous timer or event loop).
     - Periodically updates the rotation file with the elapsed time.
     - Listens for control messages via IPC.

2. **Communicating with the Background Process:**
   - When the user issues a command such as `rotate pause`, the CLI module connects to the daemon using the IPC mechanism (e.g., local TCP socket).
   - The background process receives the command, adjusts its state (e.g., pauses the timer), and updates the state file accordingly.

3. **Turn Expiry and Rotation:**
   - When the timer expires, the daemon:
     - Triggers any configured hook scripts (e.g., via the Hooks Module).
     - Rotates the team order (updates roles: Typing → Talking, etc.).
     - Writes the new state back to the rotation file.
   - Optionally, the daemon may exit after handling expiration or wait for further commands (depending on desired behavior).

4. **Process Termination:**
   - If the turn is stopped or completes, the daemon ensures all final state is written, cleans up IPC endpoints, and terminates.
   - The CLI process is not blocked by this; it simply launches the daemon and then exits.

---

## 4. Cross-Platform Considerations

- **Language Choice (Python):**  
  Python abstracts away many OS-specific details. By using Python’s standard libraries for process management, file I/O, and socket communication, you can write code that works uniformly on Linux, macOS, and Windows.

- **Daemonization:**  
  - On Unix-like systems, use a double-fork pattern or libraries such as `python-daemon` to properly detach the process.
  - On Windows, use flags with `subprocess.Popen` (like `DETACHED_PROCESS`) or other Windows-specific APIs, wrapped in a cross-platform abstraction layer.
  
- **IPC Mechanism:**  
  A TCP-based IPC (using `socket` on localhost) provides a simple and effective way to communicate between processes across all major operating systems.

---

## 5. Error Handling and Edge Cases

- **State Consistency:**  
  - Ensure that file writes are atomic or use locking mechanisms to prevent state corruption when multiple processes might access the file.
  - Clean up PID or IPC endpoint files when the daemon terminates unexpectedly.

- **Hook Failures:**  
  - Log errors when hooks fail to execute.
  - Consider a timeout or sandbox for hook execution to prevent blocking the timer.

- **User Feedback:**  
  - The CLI should return immediate feedback on command execution (e.g., “Timer paused at 1:32”) to help users understand the current state.

---

## 6. Summary

- The **CLI module** provides an intuitive interface with commands like `init`, `start`, `pause`, `resume`, `stop`, `open`, and `cat`.
- The **Timer Daemon** runs in the background, updating a simple, human-editable rotation file while managing the timer countdown.
- **Inter-Process Communication** is achieved via a cross-platform method (preferably a local TCP socket), enabling the CLI to control the daemon.
- **Hooks** allow for extensible, name-specific behaviors triggered by timer events.
- All components are implemented in Python to abstract away OS-specific details, ensuring the solution is portable across major operating systems.

This specification and architecture provide a solid foundation for developing a flexible, extensible mob timer CLI application that fits the requirements of both simplicity and cross-platform operability.
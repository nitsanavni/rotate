# Rotate

A CLI tool for mob programming rotations.

## Installation

```bash
pip install rotate-mob
```

Or with uv:

```bash
uv pip install rotate-mob
```

## Usage

### Initialize a new rotation file

```bash
rotate init [filename] [team members...]
```

This creates a new rotation file with default team members or the ones you specify:

```
5:00 / 5:00
Typing: Alice
Talking: Bob
Next: Charlie
Diana
Eva
```

### Start a timer for a rotation session

```bash
rotate start [filename] [update_interval]
```

This starts a timer daemon that will update the elapsed time in the rotation file.

### Control the timer

```bash
rotate pause [filename]  # Pause the timer
rotate resume [filename] # Resume a paused timer
rotate stop [filename]   # Stop the timer
```

### Help

```bash
rotate help
```

### Manual rotation

If you want to manually rotate team members:

```bash
cat rotation | rotate > new-rotation
```

## File Format

The rotation file format consists of:

1. First line: Timer in format `elapsed / total` where both values are in MM:SS format
2. Subsequent lines with colon: Position assignments in format `Position: Name`
3. Remaining lines: Team members without assigned positions

## Hooks

The rotate tool supports hooks that are executed when specific events occur:

1. Create a directory called `.rotate/hooks/` in your project
2. Place executable scripts in this directory with names matching the event you want to hook into
3. Currently supported hooks:
   - `expire`: Executed when the timer expires or the daemon stops

Example hook script (`.rotate/hooks/expire`):
```sh
#!/bin/sh
# This hook opens the rotation file when the timer expires
echo "Opening rotation file..."
open rotation
```

Make sure to make your hook script executable:
```sh
chmod +x .rotate/hooks/expire
```

## Requirements

- Python 3.12+
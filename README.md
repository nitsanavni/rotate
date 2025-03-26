A CLI for mobbing rotations.

## Installation

The pkg on PyPI is called `rotate-mob`.  
One way to install it is:

```bash
uv tool install rotate-mob
```

Then it's available as an executable `rotate`:

```bash
rotate help
```

## Usage

### The Rotation File

Rotation files look like this:

```
5:00 / 5:00
Typing: Alice
Talking: Bob
Next: Charlie
Diana
Eva
```

You can create a fresh one with

```bash
rotate init [filename] [team members...]
```

This creates a new rotation file with default team members or the ones you specify.


### Start the timer

```bash
rotate start [filename]
```

This starts a timer daemon that will update the elapsed time in the rotation file.

> [!TIP]
> Watch the file updated live with `watch -n 0.3 -t cat rotation`

### Other cmds

```bash
rotate pause [filename]
rotate resume [filename]
rotate stop [filename]
rotate help
```

### Manual rotation

If you want to manually rotate team members:

```bash
cat rotation | rotate > new-rotation
```

> TODO: this should be `rotate rotate`

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

# Rotate

A CLI tool for mob programming rotations.

## Usage

### Create a rotation file template

```
5:00 / 5:00
Typing: Alice
Talking: Bob
Next: Charlie
Diana
Eva
```

### Parse a rotation file to JSON

```bash
uv run parse.py < rotation.template
```

### Convert JSON back to rotation file format

```bash
uv run parse.py < rotation.template | uv run parse.py format
```

### Rotate the team

Move each team member up one position in the rotation, with the first person becoming last:

```bash
uv run rotate.py < rotation.template
```

You can chain multiple rotations:

```bash
uv run rotate.py < rotation.template | uv run rotate.py | uv run rotate.py
```

## File Format

The rotation file format consists of:

1. First line: Timer in format `elapsed / total` where both values are in MM:SS format
2. Subsequent lines with colon: Position assignments in format `Position: Name`
3. Remaining lines: Team members without assigned positions

## Requirements

- Python 3.12+
- uv package manager
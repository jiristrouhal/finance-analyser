def read_lines(raw_lines: list[str], first: int = 1, last: int = -1) -> list[list[str]]:
    """Reads lines from a text file and returns them as a list of lists of strings."""
    lines = []
    if last < 0:
        last = len(raw_lines)
    first = max(first, 1)
    assert first <= last, "First line number must be less than or equal to last line number."
    for line in raw_lines[first - 1 : last + 1]:
        line = line.strip()
        if line:
            parts = [part.strip().strip('"') for part in line.split(";")]
            lines.append(parts)
    return lines

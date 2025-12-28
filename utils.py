def read_lines(raw_lines: list[str], first: int = 1, last: int = -1) -> list[list[str]]:
    """Reads lines from a text file and returns them as a list of lists of strings."""
    lines = []
    if last < 0:
        last = len(raw_lines)
    first = max(first, 1)
    assert first <= last, "First line number must be less than or equal to last line number."
    for line in raw_lines[first - 1 : last + 1]:
        line = line.strip()
        parts = [part.strip().strip('"') for part in line.split('";"')]
        if len(parts) == 1:
            parts = [part.strip() for part in line.split(";")]
        if line:
            lines.append(parts)
    return lines


def get_column(header: list[str], column_name: str) -> int:
    """
    Finds the index of a column in the header row.
    Case insensitive, leading/trailing spaces ignored.
    """
    try:
        header = [col.lower().strip() for col in header]
        index = header.index(column_name.lower().strip())
        return index
    except ValueError:
        raise ValueError(f"Column '{column_name}' not found in header.")


def floatify(value: str) -> float:
    """Converts a string to a float, handling commas and spaces."""
    return float(value.replace(",", ".").replace(" ", ""))

import re


def read_lines(raw_lines: list[str], first: int = 1, last: int = -1) -> list[list[str]]:
    """Reads lines from a text file and returns them as a list of lists of strings."""
    lines: list[list[str]] = []
    if last < 0:
        last = len(raw_lines)
    first = max(first, 1)
    assert first <= last, "First line number must be less than or equal to last line number."
    unended_line = False
    for line in raw_lines[first - 1 : last + 1]:
        parts = _split_line(line)
        if unended_line:
            lines[-1][-1] += ", " + parts[0]
            lines[-1].extend(parts[1:])
        else:
            lines.append(parts)
        unended_line = re.fullmatch(r"\".*", parts[-1]) is not None
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


def czk_format(amount: float) -> str:
    return f"{amount:,.2f} CZK".replace(",", " ").replace(".", ",")


def _split_line(line: str) -> list[str]:
    """Splits a line into parts based on semicolon delimiter."""
    line = line.strip()
    parts = [part.strip().strip('"') for part in line.split('";"')]
    if len(parts) == 1:
        parts = [part.strip() for part in line.split(";")]
    return parts

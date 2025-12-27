import os


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


def read_csob(file_path: str) -> list[list]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
        reader = read_lines(csv_file.readlines(), first=3)
        data = [row for row in reader]
    return data


def read_reiff(file_path: str) -> list[list]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
        reader = read_lines(csv_file.readlines())
        data = [row for row in reader]
    return data


def read_creditas(file_path: str) -> list[list]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    with open(file_path, mode="r", newline="") as csv_file:
        reader = read_lines(csv_file.readlines(), first=4)
        data = [row for row in reader]
    return data


PATH = "data"


files = [os.path.join(PATH, file) for file in os.listdir(PATH)]
csv_files = [file for file in files if os.path.isfile(file) and file.endswith(".csv")]


for csv_file in csv_files:
    base = os.path.basename(csv_file).lower()
    if base.startswith("csob"):
        print(read_csob(csv_file)[0])
    elif base.lower().startswith("reiff"):
        print(read_reiff(csv_file)[0])
    elif base.lower().startswith("creditas"):
        print(read_creditas(csv_file)[0])

import os

from utils import read_lines


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


def read_unicredit(file_path: str) -> list[list]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
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
    elif base.lower().startswith("unicredit"):
        print(read_unicredit(csv_file)[0])

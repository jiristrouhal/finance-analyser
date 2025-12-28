import os
import dataclasses
from typing import Literal

from utils import read_lines, get_column, floatify
from categories import get_category


@dataclasses.dataclass(frozen=True, slots=True)
class Transaction:
    bank: Literal["csob", "reiff", "creditas", "unicredit"]
    amount: float
    category: str

    def __str__(self) -> str:
        return f"({self.bank})\t-\t{self.category}: {self.amount:.2f} CZK"


def read_csob(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            reader = read_lines(csv_file.readlines(), first=3)
            amount_col = get_column(reader[0], "Částka")
            category_col = get_column(reader[0], "Kategorie")
            return [
                Transaction("csob", floatify(row[amount_col]), row[category_col])
                for row in reader[1:]
            ]
    except Exception as e:
        print(f"Error reading CSOB Bank data: {e}")
        return []


def read_reiff(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            reader = read_lines(csv_file.readlines())
            amount_col = get_column(reader[0], "Zaúčtovaná částka")
            note_col = get_column(reader[0], "Poznámka")
            return [
                Transaction("reiff", floatify(row[amount_col]), get_category(row[note_col]))
                for row in reader[1:]
            ]
    except Exception as e:
        print(f"Error reading Reiff Bank data: {e}")
        return []


def read_creditas(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8-sig") as csv_file:
            reader = read_lines(csv_file.readlines(), first=4)
            amount_col = get_column(reader[0], "Částka")
            category_col = get_column(reader[0], "Kategorie")
            return [
                Transaction("creditas", floatify(row[amount_col]), row[category_col].rstrip('";'))
                for row in reader[1:]
            ]
    except Exception as e:
        print(f"Error reading Creditas Bank data: {e}")
        return []


def read_unicredit(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            reader = read_lines(csv_file.readlines(), first=4)
            amount_col = get_column(reader[0], "Částka")
            target_col = get_column(reader[0], "Příjemce")
            details_col = get_column(reader[0], "Detaily transakce 1")
            assert len(reader[0]) == len(
                reader[1]
            ), f"Header and row length mismatch in Unicredit CSV: {len(reader[0])} != {len(reader[1])}"
            get_unicredit_category = lambda row: get_category(row[target_col], row[details_col])
            return [
                Transaction("unicredit", floatify(row[amount_col]), get_unicredit_category(row))
                for row in reader[1:]
            ]
    except Exception as e:
        print(f"Error reading Unicredit Bank data: {e}")
        return []


DATA_PATH = "data"
files = [os.path.join(DATA_PATH, file) for file in os.listdir(DATA_PATH)]
csv_files = [file for file in files if os.path.isfile(file) and file.endswith(".csv")]


data = []
for file in csv_files:
    base = os.path.basename(file).lower()
    if base.startswith("csob"):
        data.extend(read_csob(file))
    elif base.lower().startswith("reiff"):
        data.extend(read_reiff(file))
    elif base.lower().startswith("creditas"):
        data.extend(read_creditas(file))
    if base.lower().startswith("unicredit"):
        data.extend(read_unicredit(file))


print("Transactions")
for d in data:
    print(d)

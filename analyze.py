import os
import dataclasses
from collections import defaultdict
from typing import Literal, get_args

from utils import read_lines, get_column, floatify
from categories import get_category, replace_category


BankName = Literal["csob", "reiff", "creditas", "unicredit"]


INVALID_CATEGORIES = {
    "Nezařazeno",
    "Nezařazené",
    "Odchozí nezatříděná",
    "Příjem",
    "",
}


def extract_category(row: list[str], category_col: int, *other_cols: int) -> str:
    """Extracts the category from the row based on the category name and keys."""
    # First try to read the category directly from the specified column
    assert all(
        isinstance(col, int) for col in (category_col, *other_cols)
    ), "Column indices must be integers"
    category = row[category_col].rstrip(';"')
    if category and category not in INVALID_CATEGORIES:
        return replace_category(category)
    # If not found, use the keys to determine the category
    if not other_cols:
        return "Nezařazené"

    row_keys = [row[col] for col in other_cols]
    return get_category(row[category_col], *row_keys)


@dataclasses.dataclass(frozen=True, slots=True)
class Transaction:
    bank: BankName
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
                Transaction(
                    "csob",
                    floatify(row[amount_col]),
                    extract_category(
                        row,
                        category_col,
                        get_column(reader[0], "jméno protistrany"),
                        get_column(reader[0], "vlastní poznámka"),
                        get_column(reader[0], "zpráva"),
                    ),
                )
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
            counterparty_col = get_column(reader[0], "Název protiúčtu")
            return [
                Transaction(
                    "reiff",
                    floatify(row[amount_col]),
                    get_category(row[note_col], row[counterparty_col]),
                )
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
                Transaction(
                    "creditas",
                    floatify(row[amount_col]),
                    extract_category(
                        row,
                        category_col,
                        get_column(reader[0], "Název protiúčtu"),
                        get_column(reader[0], "Protiúčet"),
                    ),
                )
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


for file in csv_files:
    bank = os.path.basename(file).split("_")[0].lower()
    if bank not in get_args(BankName):
        raise ValueError(f"\033[31mUnknown bank file format: {file}\033[0m")


data: list[Transaction] = []
for file in csv_files:
    base = os.path.basename(file).lower()
    if base.startswith("csob"):
        data.extend(read_csob(file))
    elif base.lower().startswith("reiff"):
        data.extend(read_reiff(file))
    elif base.lower().startswith("creditas"):
        data.extend(read_creditas(file))
    elif base.lower().startswith("unicredit"):
        data.extend(read_unicredit(file))


totals: dict[str, float] = defaultdict(float)

for transaction in data:
    totals[transaction.category] += transaction.amount


total_incomes = {k: v for k, v in totals.items() if v >= 0}
total_expenses = {k: v for k, v in totals.items() if v < 0}


total = sum(totals.values())
print(f"Overall total: {total:.2f} CZK\n")


print("Příjmy:\n-------")
for category, amount in total_incomes.items():
    print(f"- {category}: {amount:.2f} CZK")
print("\nVýdaje:\n-------")
for category, amount in total_expenses.items():
    print(f"- {category}: {amount:.2f} CZK")

# print("Transactions")
# for d in data:
#     print(d)

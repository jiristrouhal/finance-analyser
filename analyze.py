import os
import dataclasses

from utils import read_lines, get_column


@dataclasses.dataclass(frozen=True, slots=True)
class Transaction:
    amount: float
    category: str

    def __str__(self) -> str:
        return f"{self.category}: {self.amount:.2f} CZK"


def load_transactions(data: list[list[str]], cols: "Columns") -> list[Transaction]:
    return [
        Transaction(float(row[cols.AMOUNT].replace(",", ".")), row[cols.CATEGORY]) for row in data
    ]


@dataclasses.dataclass(frozen=True, slots=True)
class Columns:
    AMOUNT: int
    CATEGORY: int

    @classmethod
    def get_cols(cls, header: list[str], amount_name: str, category_name: str) -> "Columns":
        amount_col = get_column(header, amount_name)
        category_col = get_column(header, category_name)
        return Columns(AMOUNT=amount_col, CATEGORY=category_col)


def read_csob(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            reader = read_lines(csv_file.readlines(), first=3)
            cols = Columns.get_cols(reader[0], "Částka", "Kategorie")
            return load_transactions(reader[1:], cols)
    except Exception as e:
        print(f"Error reading CSOB Bank data: {e}")
        return []


def read_reiff(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            reader = read_lines(csv_file.readlines())
            cols = Columns.get_cols(reader[0], "Zaúčtovaná částka", "Kategorie transakce")
            return load_transactions(reader[1:], cols)
    except Exception as e:
        print(f"Error reading Reiff Bank data: {e}")
        return []


def read_creditas(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8-sig") as csv_file:
            reader = read_lines(csv_file.readlines(), first=4)
            cols = Columns.get_cols(reader[0], "Částka", "Kategorie")
            return load_transactions(reader[1:], cols)
    except Exception as e:
        print(f"Error reading Creditas Bank data: {e}")
        return []


def read_unicredit(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            reader = read_lines(csv_file.readlines(), first=4)
            cols = Columns.get_cols(reader[0], "Částka", "Kategorie")
            return load_transactions(reader[1:], cols)
    except Exception as e:
        print(f"Error reading Unicredit Bank data: {e}")
        return []


PATH = "data"


files = [os.path.join(PATH, file) for file in os.listdir(PATH)]
csv_files = [file for file in files if os.path.isfile(file) and file.endswith(".csv")]


for csv_file in csv_files:
    base = os.path.basename(csv_file).lower()
    if base.startswith("csob"):
        data = read_csob(csv_file)
    elif base.lower().startswith("reiff"):
        data = read_reiff(csv_file)
    elif base.lower().startswith("creditas"):
        data = read_creditas(csv_file)
    elif base.lower().startswith("unicredit"):
        data = read_unicredit(csv_file)
    for d in data:
        print(d)

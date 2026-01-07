import os
import dataclasses
from typing import Literal, get_args

from utils import read_lines, get_column, floatify, czk_format
from categories import get_category, replace_category


BankName = Literal["csob", "raiffeisenbank", "creditas", "unicreditbank"]


BANK_NAMES = set(get_args(BankName))

DATA_PATH = "data"

INVALID_CATEGORIES = {
    "Nezařazeno",
    "Nezařazené",
    "Odchozí nezatříděná",
    "Bankovní transakce",
    "Služby",
    "Příjem",
    "",
}


@dataclasses.dataclass(frozen=True, slots=True)
class Transaction:
    bank: BankName
    amount: float
    category: str
    info: str = ""
    date: str = ""

    def __str__(self) -> str:
        return (
            f"({self.bank})\t-\t{self.category}: {self.amount:.2f} ({self.info}, {self.date}) CZK"
        )


def load_data(*csv_paths: str) -> list[Transaction]:
    data: list[Transaction] = []
    for file in csv_paths:
        base = os.path.basename(file).lower()
        if base.startswith("csob"):
            data.extend(_read_csob(file))
        elif base.lower().startswith("raif"):
            data.extend(_read_raiff(file))
        elif base.lower().startswith("cred"):
            data.extend(_read_creditas(file))
        elif base.lower().startswith("unic"):
            data.extend(_read_unicredit(file))
    return data


def collect_csv_paths() -> list[str]:
    paths = [os.path.join(DATA_PATH, path) for path in os.listdir(DATA_PATH)]
    csv_paths = [path for path in paths if os.path.isfile(path) and path.endswith(".csv")]
    dir_paths = [path for path in paths if os.path.isdir(path)]
    for dir_path in dir_paths:
        dir_files = [
            os.path.join(dir_path, path)
            for path in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, path)) and path.endswith(".csv")
        ]
        csv_paths.extend(dir_files)
    for csv_path in csv_paths:
        bank = os.path.basename(csv_path).split("_")[0].lower()
        if not any(bank in bn for bn in BANK_NAMES):
            raise ValueError(f"\033[31mUnknown bank file format: {csv_path}\033[0m")
    return csv_paths


def _extract_category(row: list[str], category_col: int, *other_cols: int) -> str:
    """Extracts the category from the row based on the category name and keys."""
    # First try to read the category directly from the specified column
    assert all(
        isinstance(col, int) for col in (category_col, *other_cols)
    ), "Column indices must be integers"

    category = ""
    if other_cols:
        row_keys = [row[col] for col in other_cols]
        category = get_category(*row_keys)
    if not category or ("Nezařazeno" in category):
        category = row[category_col].rstrip(';"')
    category = replace_category(category.strip())
    return category or "Nezařazené"


def _read_csob(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            reader = read_lines(csv_file.readlines(), first=3)
            amount_col = get_column(reader[0], "Částka")
            category_col = get_column(reader[0], "Kategorie")
            counterparty_number_col = get_column(reader[0], "číslo protiúčtu")
            counterparty_col = get_column(reader[0], "jméno protistrany")
            date_col = get_column(reader[0], "datum zaúčtování")
            msg_col = get_column(reader[0], "zpráva")
            return [
                Transaction(
                    "csob",
                    floatify(row[amount_col]),
                    _extract_category(
                        row,
                        category_col,
                        get_column(reader[0], "jméno protistrany"),
                        get_column(reader[0], "vlastní poznámka"),
                        msg_col,
                        get_column(reader[0], "číslo protiúčtu"),
                    ),
                    info=row[counterparty_col] or row[counterparty_number_col] or row[msg_col],
                    date=row[date_col],
                )
                for row in reader[1:]
            ]
    except Exception as e:
        print(f"Error reading CSOB Bank data: {e}")
        return []


def _read_raiff(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            reader = read_lines(csv_file.readlines())
            amount_col = get_column(reader[0], "Zaúčtovaná částka")
            note_col = get_column(reader[0], "Poznámka")
            counterparty_col = get_column(reader[0], "Název protiúčtu")
            counterparty_account_col = get_column(reader[0], "Číslo protiúčtu")
            date_col = get_column(reader[0], "Datum zaúčtování")
            name_of_trader_col = get_column(reader[0], "Název obchodníka")
            return [
                Transaction(
                    "raiffeisenbank",
                    floatify(row[amount_col]),
                    get_category(
                        row[name_of_trader_col],
                        row[note_col],
                        row[counterparty_col],
                        row[counterparty_account_col],
                    ),
                    info=row[counterparty_col] or row[note_col] or row[counterparty_account_col],
                    date=row[date_col],
                )
                for row in reader[1:]
            ]
    except Exception as e:
        print(f"Error reading Reiff Bank data: {e}")
        return []


def _read_creditas(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8-sig") as csv_file:
            reader = read_lines(csv_file.readlines(), first=4)
            amount_col = get_column(reader[0], "Částka")
            counterparty_col = get_column(reader[0], "Protiúčet")
            counterparty_name_col = get_column(reader[0], "Název protiúčtu")
            date_col = get_column(reader[0], "Datum zaúčtování")
            note_col = get_column(reader[0], "Zpráva pro protistranu")
            return [
                Transaction(
                    "creditas",
                    floatify(row[amount_col]),
                    _extract_category(
                        row,
                        get_column(reader[0], "Kategorie"),
                        counterparty_name_col,
                        counterparty_col,
                        note_col,
                    ),
                    info=row[counterparty_name_col] or row[counterparty_col] or row[note_col],
                    date=row[date_col],
                )
                for row in reader[1:]
            ]
    except Exception as e:
        print(f"Error reading Creditas Bank data: {e}")
        return []


def _read_unicredit(file_path: str) -> list[Transaction]:
    """Reads a CSV file and returns its content as a list of dictionaries."""
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            reader = read_lines(csv_file.readlines(), first=4)
            amount_col = get_column(reader[0], "Částka")
            target_col = get_column(reader[0], "Příjemce")
            details_col = get_column(reader[0], "Detaily transakce 1")
            date_col = get_column(reader[0], "Datum rezervace")
            assert len(reader[0]) == len(
                reader[1]
            ), f"Header and row length mismatch in Unicredit CSV: {len(reader[0])} != {len(reader[1])}"
            get_unicredit_category = lambda row: get_category(row[target_col], row[details_col])
            return [
                Transaction(
                    "unicreditbank",
                    floatify(row[amount_col]),
                    get_unicredit_category(row),
                    info=(row[target_col] or row[details_col]).strip('", '),
                    date=row[date_col],
                )
                for row in reader[1:]
            ]
    except Exception as e:
        print(f"Error reading Unicredit Bank data: {e}")
        return []

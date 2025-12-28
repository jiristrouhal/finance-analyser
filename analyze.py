import json
import os
from collections import defaultdict

from read import load_data, czk_format, BANK_NAMES


DATA_PATH = "data"
paths = [os.path.join(DATA_PATH, path) for path in os.listdir(DATA_PATH)]
csv_paths = [path for path in paths if os.path.isfile(path) and path.endswith(".csv")]
for csv_path in csv_paths:
    bank = os.path.basename(csv_path).split("_")[0].lower()
    if bank not in BANK_NAMES:
        raise ValueError(f"\033[31mUnknown bank file format: {csv_path}\033[0m")


data = load_data(*csv_paths)

totals: dict[str, float] = defaultdict(float)

for transaction in data:
    totals[transaction.category] += transaction.amount

total_incomes = {
    k: v for k, v in sorted(totals.items(), key=lambda item: item[1], reverse=True) if v > 0
}
total_expenses = {k: v for k, v in sorted(totals.items(), key=lambda item: item[1]) if v < 0}
zeros = {k: v for k, v in totals.items() if v == 0}


total_income = sum(total_incomes.values()) if total_incomes else 0.0
print(f"Příjmy celkem:     {czk_format(total_income):>30}")
total_expense = sum(total_expenses.values()) if total_expenses else 0.0
print(f"Výdaje celkem:     {czk_format(total_expense):>30}")
total = sum(totals.values()) if totals else 0.0
print(f"Bilance celkem:    {czk_format(total):>30}\n")

print("Příjmy:\n-------")
for category, amount in total_incomes.items():
    print(f"- {category:<30} {czk_format(amount):>15} {amount / total_income * 100:>6.1f}%")
print("\nVýdaje:\n-------")
for category, amount in total_expenses.items():
    print(f"- {category:<30} {czk_format(amount):>15} {amount / total_expense * 100:>6.1f}%")
print("\nNeutrální kategorie (0 CZK):\n-------")
for category in zeros.keys():
    print(f"- {category}")

with open("summary.json", "w", encoding="utf-8") as summary_file:
    json.dump(
        {
            "incomes": {k: round(v, 2) for k, v in total_incomes.items()},
            "expenses": {k: round(v, 2) for k, v in total_expenses.items()},
            "zeros": list(zeros.keys()),
        },
        summary_file,
        ensure_ascii=False,
        indent=4,
    )

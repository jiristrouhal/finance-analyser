import json
import sys

from read import load_data, czk_format, collect_csv_paths
from process import process_transactions


csv_paths = collect_csv_paths()
data = load_data(*csv_paths)
days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
result = process_transactions(data, days=days)


total_income = sum(result.total_incomes.values()) if result.total_incomes else 0.0
print(f"Příjmy celkem:     {czk_format(total_income):>30}")
total_expense = sum(result.total_expenses.values()) if result.total_expenses else 0.0
print(f"Výdaje celkem:     {czk_format(total_expense):>30}")
total = sum(result.total_incomes.values()) + sum(result.total_expenses.values())
print(f"Bilance celkem:    {czk_format(total):>30}\n")


print("Příjmy:\n-------")
for category, amount in result.total_incomes.items():
    print(f"- {category:<30} {czk_format(amount):>15} {amount / total_income * 100:>6.1f}%")
print("\nVýdaje:\n-------")
for category, amount in result.total_expenses.items():
    print(f"- {category:<30} {czk_format(amount):>15} {amount / total_expense * 100:>6.1f}%")
print("\nNeutrální kategorie (0 CZK):\n-------")
for category in result.zeros.keys():
    print(f"- {category}")

with open("summary.json", "w", encoding="utf-8") as summary_file:
    json.dump(
        {
            "incomes": {k: round(v, 2) for k, v in result.total_incomes.items()},
            "expenses": {k: round(v, 2) for k, v in result.total_expenses.items()},
            "zeros": list(result.zeros.keys()),
        },
        summary_file,
        ensure_ascii=False,
        indent=4,
    )

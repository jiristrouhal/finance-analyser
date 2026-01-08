import json
import sys
from collections import defaultdict

from read import load_data, czk_format, collect_csv_paths, Transaction
from process import process_transactions


csv_paths = collect_csv_paths()
data = load_data(*csv_paths)
transfers: list[Transaction] = [t for t in data if t.category == "Převod"]
orig_transfers = transfers.copy()
n = len(transfers)

i = 0
while i < len(transfers):
    match_found = False
    j = i + 1
    while j < len(transfers):
        if transfers[i].amount == -transfers[j].amount and transfers[i] != transfers[j]:
            match_found = True
            break
        else:
            j += 1
    if match_found:
        transfers.pop(j)
        transfers.pop(i)
    else:
        i += 1


if transfers:
    print(f"Varování: Nalezeno {n - len(transfers)} spárovaných převodů z celkem {n} převodů.")
    print("Následující převody nebyly spárovány, nelze pokračovat.")
    for t in transfers:
        print(f"- {t.bank}: {czk_format(t.amount)} dne {t.date}, info: {t.info}")
    print()
    exit(1)


days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
result = process_transactions(data, days=days)


total_income = sum(result.total_incomes.values()) if result.total_incomes else 0.0
print(f"Příjmy celkem:     {czk_format(total_income):>30}")
total_expense = sum(result.total_expenses.values()) if result.total_expenses else 0.0
print(f"Výdaje celkem:     {czk_format(total_expense):>30}")
total = sum(result.total_incomes.values()) + sum(result.total_expenses.values())
print(f"Bilance celkem:    {czk_format(total):>30}\n")


REST_RATIO = 0.1
cum_amount = 0.0
below_threshold = True
print("Příjmy:\n-------")
for category, amount in result.total_incomes.items():
    if below_threshold:
        if cum_amount > (1 - REST_RATIO) * total_income:
            print(f"------------ Zbylých < 10 % příjmů ------------")
            below_threshold = False
        else:
            cum_amount += amount

    print(f"- {category:<30} {czk_format(amount):>15} {amount / total_income * 100:>6.1f}%")
cum_amount = 0.0
below_threshold = True
print("\nVýdaje:\n-------")
for category, amount in result.total_expenses.items():
    if below_threshold:
        if cum_amount < (1 - REST_RATIO) * total_expense:
            print(f"------------ Zbylých < 10 % výdajů ------------")
            below_threshold = False
        else:
            cum_amount += amount
    print(f"- {category:<30} {czk_format(amount):>15} {amount / total_expense * 100:>6.1f}%")
print("\nNeutrální kategorie (0 CZK):\n-------")
for category in result.zeros.keys():
    print(f"- {category}")


with open("details.json", "w", encoding="utf-8") as details_file:

    data_dict = defaultdict(list)
    for transaction in data:
        data_dict[transaction.category].append(
            {
                "banka": transaction.bank,
                "částka": czk_format(round(transaction.amount, 2)),
                "info": transaction.info,
                "datum": transaction.date,
            }
        )

    json.dump(data_dict, details_file, ensure_ascii=False, indent=2)


with open("summary.json", "w", encoding="utf-8") as summary_file:
    json.dump(
        {
            "celkem": {
                "příjmy": round(total_income, 2),
                "výdaje": round(total_expense, 2),
                "zůstatek": round(total, 2),
            },
            "příjmy": {k: round(v, 2) for k, v in result.total_incomes.items()},
            "výdaje": {k: round(v, 2) for k, v in result.total_expenses.items()},
            "neutrální": list(result.zeros.keys()),
        },
        summary_file,
        ensure_ascii=False,
        indent=4,
    )

import dataclasses
from collections import defaultdict

from read import Transaction


@dataclasses.dataclass
class Result:
    total_incomes: dict[str, float]
    total_expenses: dict[str, float]
    zeros: dict[str, float]


def process_transactions(data: list[Transaction], days: int) -> Result:
    totals: dict[str, float] = defaultdict(float)

    for transaction in data:
<<<<<<< HEAD
        totals[transaction.category] += transaction.amount * (30.0 / days)
=======
        totals[transaction.category] += transaction.amount * ((365 / 12.0) / days)
>>>>>>> 40d272d0a6868a73840f3e151b1ee9afe35dbe39

    total_incomes = {
        k: v for k, v in sorted(totals.items(), key=lambda item: item[1], reverse=True) if v > 0
    }
    total_expenses = {k: v for k, v in sorted(totals.items(), key=lambda item: item[1]) if v < 0}
    zeros = {k: v for k, v in totals.items() if abs(v) < 0.01}

    return Result(
        total_incomes=total_incomes,
        total_expenses=total_expenses,
        zeros=zeros,
    )

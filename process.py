import dataclasses
import json
import os
from collections import defaultdict

from read import Transaction
from constants import MAPPING_PATH as _MAPPING_PATH


with open(os.path.join(_MAPPING_PATH, "mapping.json"), "r", encoding="utf-8") as f:
    _TO_SKIP = set(dict(json.load(f))["skip"])


@dataclasses.dataclass
class Result:
    total_incomes: dict[str, float]
    total_expenses: dict[str, float]
    zeros: dict[str, float]


def process_transactions(data: list[Transaction], days: int) -> Result:
    totals: dict[str, float] = defaultdict(float)

    for transaction in data:
        if transaction.category in _TO_SKIP:
            continue
        totals[transaction.category] += transaction.amount * (30 / days)

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

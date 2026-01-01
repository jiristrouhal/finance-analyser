import sys
import json


def combine_summaries(*paths: str) -> dict:
    combined_summary: dict[str, dict | list] = {}
    for path in paths:
        with open(path, "r", encoding="utf-8") as file:
            summary = json.load(file)
            add_summary(combined_summary, summary)
    combined_summary["zeros"] = list(combined_summary["zeros"])
    return combined_summary


def add_summary(combined: dict, summary: dict) -> None:
    combined["incomes"] = combined.get("incomes", {})
    combined["expenses"] = combined.get("expenses", {})
    for key in ["incomes", "expenses"]:
        if key not in combined:
            combined[key] = {}
        for category, amount in summary.get(key, {}).items():
            if category in combined[key]:
                combined[key][category] = round(amount + combined[key][category], 2)
            else:
                combined[key][category] = amount
    if "zeros" not in combined:
        combined["zeros"] = set()
    if not "totals" in combined:
        combined["totals"] = {"incomes": 0.0, "expenses": 0.0, "balance": 0.0}
    for total_key in ["incomes", "expenses", "balance"]:
        combined["totals"][total_key] = round(
            combined["totals"].get(total_key, 0.0) + summary.get("totals", {}).get(total_key, 0.0),
            2,
        )
    combined["zeros"].update(summary.get("zeros", []))


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python comb.py <summary1.json> <summary2.json> ...")
        sys.exit(1)

    combined = combine_summaries(*sys.argv[1:])

    json_output_path = "combined_summary.json"
    with open(json_output_path, "w", encoding="utf-8") as json_file:
        json.dump(combined, json_file, ensure_ascii=False, indent=4)

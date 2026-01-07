import sys
import json


def combine_summaries(*paths: str) -> dict:
    combined_summary: dict[str, dict | list] = {}
    for path in paths:
        with open(path, "r", encoding="utf-8") as file:
            summary = json.load(file)
            add_summary(combined_summary, summary)
    combined_summary["neutrální"] = list(combined_summary["neutrální"])
    return combined_summary


def add_summary(combined: dict, summary: dict) -> None:
    combined["příjmy"] = combined.get("příjmy", {})
    combined["výdaje"] = combined.get("výdaje", {})
    for key in ["příjmy", "výdaje"]:
        if key not in combined:
            combined[key] = {}
        for category, amount in summary.get(key, {}).items():
            if category in combined[key]:
                combined[key][category] = round(amount + combined[key][category], 2)
            else:
                combined[key][category] = amount
    if "neutrální" not in combined:
        combined["neutrální"] = set()
    if not "celkem" in combined:
        combined["celkem"] = {"příjmy": 0.0, "výdaje": 0.0, "balance": 0.0}
    for total_key in ["příjmy", "výdaje", "balance"]:
        combined["celkem"][total_key] = round(
            combined["celkem"].get(total_key, 0.0) + summary.get("celkem", {}).get(total_key, 0.0),
            2,
        )
    combined["neutrální"].update(summary.get("neutrální", []))


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python comb.py <summary1.json> <summary2.json> ...")
        sys.exit(1)

    combined = combine_summaries(*sys.argv[1:])

    json_output_path = "combined_summary.json"
    with open(json_output_path, "w", encoding="utf-8") as json_file:
        json.dump(combined, json_file, ensure_ascii=False, indent=4)

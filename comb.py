import sys
import json


def combine_summaries(*paths: str) -> str:
    combined_summary = {}
    for path in paths:
        with open(path, "r") as file:
            summary = json.load(file)
            combined_summary.update(summary)
    return json.dumps(combined_summary)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python comb.py <summary1.json> <summary2.json> ...")
        sys.exit(1)

    combined = combine_summaries(*sys.argv[1:])

    json_output_path = "combined_summary.json"
    with open(json_output_path, "w") as json_file:
        json_file.write(combined)

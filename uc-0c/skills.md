# skills.md — UC-0C Budget Growth Tracker

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates proper columns, and actively reports the total count of null values alongside identifying which exact rows contain them before returning the parsed dataset.
    input: File path (string)
    output: A list of row dictionaries representing the CSV data.
    error_handling: Raise a FileNotFoundError if the CSV does not exist. Do not crash on blank lines.

  - name: compute_growth
    description: Takes a specified ward, category, and growth_type context to construct a chronological table calculating percentage growth between periods alongside transparent mathematical formulas.
    input: A dataset (list of dicts), a ward name (string), a category name (string), and a formula type (string).
    output: A list of dicts representing calculated rows for CSV output.
    error_handling: System refusal (raise ValueError) if ward or category are not passed (aggregation attempt) or if the growth type is unrecognized or missing. Gracefully handle division by zero or broken calculation chains due to intermediate null data points.

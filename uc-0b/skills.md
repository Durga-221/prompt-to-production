# skills.md — UC-0B Leave Policy Summarizer

skills:
  - name: retrieve_policy
    description: Parses and loads the .txt policy file and returns its content as structured, numbered sections.
    input: File path (string)
    output: A dictionary mapping clause numbers (e.g., '2.3') to their full text content.
    error_handling: Raise a FileNotFoundError if the file cannot be accessed. Ignore unnumbered introductory paragraphs.

  - name: summarize_policy
    description: Takes structured clauses and produces a compliant summary adhering to strict condition preservation rules.
    input: A dictionary of structured clauses.
    output: A single string containing the markdown-formatted summary.
    error_handling: Return "[VERBATIM] text" if the logic detects risk of meaning loss.

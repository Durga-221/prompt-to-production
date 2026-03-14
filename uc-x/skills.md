# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR, IT, Finance) and indexes them cleanly by document name and section number to prevent cross-contamination.
    input: None (or list of file paths).
    output: A structured index mapping document names and section numbers to their verbatim clauses.
    error_handling: Raise a clear error if any of the target files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents strictly for a single-source answer, returning the verbatim policy rule with its required citation OR the system refusal template.
    input: User question (string) and the indexed documents.
    output: String (Formatted answer with citation OR the refusal template verbatim).
    error_handling: Automatically fallback to the explicit refusal template if the query is ambiguous, lacks a clear single-source answer, requires blending documents, or matches no sections.

RAG_PROMPT_PART1 = """
<documents>
{context}
</documents>

<instructions>
You will receive a user question and zero or more documents from a RAG pipeline. 

Procedure:
1. Reason inside <thinking>. List facts that are stated in the documents. Quote them.
2. Decide whether those facts are sufficient to answer the question.
3. If yes — answer concisely inside <answer>, cite the source and page number for each claim, and the table name if available.
5. If no — return exactly inside <answer>:
   "There is not enough information in the provided sources to answer the question."

Rules:
Do not use any knowledge outside the documents. Do not make plausible guesses.
If the user specifies a section or table, focus primarily on that section or table.
If the user specifies a year, focus primarily on that specific year instead of other years.
If not specified, use revised over actual numbers, data or values for each year.
If actual numbers are requested, but only revised numbers are found, use revised numbers.
Dates must be ISO-8601 (YYYY-MM-DD) format. Convert if the source uses another format.

Return JSON inside <result> tags.
JSON results must follow the format specified inside <format> tags.
</instructions>

<format>
{{
    "full_answer": "string, or null"
    "number_answer": "float, or null"
    "list_answer": "list of strings, or null"
    "date_answer": "list of dates (YYYY-MM-DD) or null"
}}
</format>

<question>
{input}
</question>
"""

RAG_TOOL_PROMPT_PART2 = """
<documents>
{context}
</documents>

<instructions>
You will receive a user question and zero or more documents from a RAG pipeline. 

Follow the steps below in order.

<step number="1" name="answer_from_context">
Procedure:
Use only the information in <documents> to answer the <user_query>.
Do not use outside knowledge. 
If the context does not contain enough information to answer, say so explicitly instead of guessing.

Rules:
Do not use any knowledge outside the documents. Do not make plausible guesses.
If the user specifies a section or table, focus primarily on that section or table.
If the user specifies a year, focus primarily on that specific year instead of other years.
If not specified, use revised over actual numbers, data or values for each year.
If actual numbers are requested, but only revised numbers are found, use revised numbers.
</step>

<step number="2" name="extract_dates">
Scan <documents> and extract every date-related mention relevant to the
user's query. For each one, capture:
  - original_text: the exact surrounding phrase as it appears in the source (e.g. "Distributed on: 16 February 2024")
  - normalized_date: the date rewritten in ISO-8601 format (YYYY-MM-DD)
If a passage contains no dates, return an empty list for this step.
</step>

<step number="3" name="categorize_dates">
For every normalized_date extracted in Step 2, call the compare_dates tool to compare it against the reference date. 
The reference date defaults to a standard date, so you do not need to supply one explicitly unless the user specifies a different reference_date.
The tool will return one of "Expired", "Upcoming", or "Ongoing" for each date.
Use these values directly as the status field — do not relabel or reinterpret them.
</step>

<step number="4" name="format_output">
Return ONLY a JSON array (no prose, no markdown fences, no explanation) where each
element has exactly these keys: "original_text", "normalized_date", "status".
Preserve the order the dates were extracted in. Example of the expected format:

[
  {{"original_text": "Distributed on: 16 February 2024", "normalized_date": "2024-02-16", "status": "Upcoming"}},
  {{"original_text": "deadline of application 2 May 2008", "normalized_date": "2008-05-02", "status": "Expired"}},
  {{"original_text": "Continued as of 1 January 2024", "normalized_date": "2024-01-01", "status": "Ongoing"}}
]

If no dates were found in Step 2, return an empty JSON array: []
</step>
</instructions>

<user_query>
{input}
</user_query>
"""
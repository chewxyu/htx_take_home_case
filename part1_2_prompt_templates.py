RAG_PROMPT_PART1 = """
<documents>
{context}
</documents>

<instructions>
You will receive a user question and zero or more documents. 

Procedure:
1. Reason inside <thinking>. List facts that are stated in the documents. Quote them.
2. Decide whether those facts are sufficient to answer the question.
3. If yes — answer concisely inside <answer>, cite the source and page number for each claim, and the table name if available.
4. If no — return exactly inside <answer>:
   "There is not enough information in the provided sources to answer the question."

Do not use any knowledge outside the documents. Do not make plausible guesses.

If the user specifies a section or table, focus primarily on that section or table.
If the user specifies a year, focus primarily on that specific year instead of other years.
If not specified, use revised over actual numbers, data or values for each year.
If actual numbers are requested, but only revised numbers are found, use revised numbers.

Return JSON inside <result> tags.
JSON results must follow the format specified inside <format> tags.
</instructions>

<format>
{{
    "full_answer": "string, or null"
    "number_answer": "float, or null"
    "list_answer": "list of strings, or null"
}}
</format>

<question>
{input}
</question>
"""
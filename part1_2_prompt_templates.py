RAG_PROMPT_PART1 = """
<documents>
{rag_docs}
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
Always use revised numbers, data or valuees estimated numbers for that same year, unless specified.

Return JSON inside <result> tags.
JSON results must follow the format specified inside <format> tags.
</instructions>

<format>
{
    "answer": "string, float, or null"
}
</format>

<question>
{query}
</question>
"""

# <format>
# {
#   "is_meeting": true,
#   "title": "string",
#   "start": "ISO-8601 with timezone",
#   "end": "ISO-8601 with timezone",
#   "attendees": ["string"],
#   "location": "string or null",
#   "notes": "string or null"
# }
# </format>

# <format>
# {
#   "vendor_name": "string or null",
#   "vendor_tax_id": "string or null",
#   "invoice_number": "string or null",
#   "issue_date": "YYYY-MM-DD or null",
#   "due_date": "YYYY-MM-DD or null",
#   "currency": "ISO-4217 code",
#   "subtotal": 0.0,
#   "tax": 0.0,
#   "total": 0.0,
#   "totals_inconsistent": false,
#   "line_items": [
#     { "description": "string", "quantity": 1, "unit_price": 0.0, "amount": 0.0 }
#   ]
# }
# </format>

# - Dates must be ISO-8601 (YYYY-MM-DD). Convert if the source uses another format
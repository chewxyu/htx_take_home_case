from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage


class IntentClassification(BaseModel):
    intent_summary: str = Field(
        description='A concise summary of what the user is asking for.'
    )
    requires_revenue_agent: bool = Field(
        description='True if the query needs information on government revenue, income, taxes, vehicle quota premiums, levies, charges, receipts, duties, statutory board contributions, capitalisation of infrastrucutre, or investment returns.'
    )
    requires_expenditure_agent: bool = Field(
        description='True if the query needs information on government spending, allocations, funds, budget outlays, healthcare, infrastructure development, fund top ups, interest costs, loan expenses, depreciation of infrastructure, or inflationary pressures.'
    )


def llm_detect_intents(llm, query):
    structured_llm = llm.with_structured_output(IntentClassification)

    intent_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=(
            """
            <instructions>
            You are the supervisor of a multi-agent system that answers questions about government finances using documents from a RAG pipeline.
            You have two specialized agents available:
            1. Revenue Agent - identifies and analyzes information on government revenue to answer queries.
            (e.g. income, taxes, vehicle quota premiums, levies, charges, receipts, duties, statutory board contributions, capitalisation of infrastrucutre, or investment returns).
            2. Expenditure Agent - identifies and analyzes information on government spending to answer queries.
            (e.g. allocations, funds, budget outlays, healthcare, infrastructure development, fund top ups, interest costs, loan expenses, depreciation of infrastructure, or inflationary pressures).

            Read the user query and determine which if each of the agents is needed to answer it.
            A query may require one or more agents.
            </instructions>
            """)
        ),
        ('human', '{user_query}')
    ])

    chain = intent_prompt | structured_llm
    result = chain.invoke({'user_query': query})

    return result


def rag_retrieve_context(query, rag_retriever):
    rag_results = rag_retriever.invoke(query)

    context_parts=[]
    for result in rag_results:
        source = result.metadata.get('source', 'unknown source')
        page = result.metadata.get('page', '?')
        context_parts.append(f'[Source: {source}, Page: {page}]\n{result.page_content}')
    context_str = '\n\n'.join(context_parts)
    return context_str


def llm_revenue_agent(llm, query, rag_retriever):
    rag_context = rag_retrieve_context(query, rag_retriever)

    revenue_agent_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=(
            """
            <instructions>
            You are the Revenue Agent in a multi-agent government finance system.
            Your role is to identify and extract information on government revenue using only the provided context.
            (e.g. income, taxes, vehicle quota premiums, levies, charges, receipts, duties, statutory board contributions, capitalisation of infrastrucutre, or investment returns).
            Precision matters: report every figure to the correct amount exactly as it appears in the context, including currency, units (e.g. thousands, millions), and fiscal year or period. Do not round, estimate, or recalculate figures.
            
            Procedure:
            1. Reason inside <thinking>. List facts that are stated in the documents. Quote them.
            2. If the context does not contain enough information to answer, say so explicitly instead of guessing.
            3. Answer the <user_query> consisely based on reasoning, cite the source and page number for each claim, and the table name if available. 

            Rules:
            If the user specifies a section or table, focus primarily on that section or table.
            If the user specifies a year, focus primarily on that specific year instead of other years.
            If not specified, use revised over actual numbers, data or values for each year.
            Dates must be ISO-8601 (YYYY-MM-DD) format. Convert if the source uses another format.
            </instructions>
            """)
        ),
        ('human', 
        """
        <context>
        {rag_context}
        </context>
        <user_query>
        {user_query}
        </user_query>
        """
        )
    ])
    
    chain = revenue_agent_prompt | llm
    result = chain.invoke({
        'user_query': query,
        'rag_context': rag_context
    })

    return result


def llm_expenditure_agent(llm, query, rag_retriever):
    rag_context = rag_retrieve_context(query, rag_retriever)

    expenditure_agent_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=(
            """
            <instructions>
            You are the Expenditure Agent in a multi-agent government finance system.
            Your role is to identify and extract information on government spending using only the provided context.
            (e.g. allocations, funds, budget outlays, healthcare, infrastructure development, fund top ups, interest costs, loan expenses, depreciation of infrastructure, or inflationary pressures).
            Precision matters: report every figure to the correct amount exactly as it appears in the context, including currency, units (e.g. thousands, millions), and fiscal year or period. Do not round, estimate, or recalculate figures.
            If a figure's precision or scope is ambiguous in the context, note the ambiguity rather than resolving it yourself.
            
            Procedure:
            1. Reason inside <thinking>. List facts that are stated in the documents. Quote them.
            2. If the context does not contain enough information to answer, say so explicitly instead of guessing.
            3. Answer the <user_query> consisely based on reasoning, cite the source and page number for each claim, and the table name if available. 
            
            Rules:
            If the user specifies a section or table, focus primarily on that section or table.
            If the user specifies a year, focus primarily on that specific year instead of other years.
            If not specified, use revised over actual numbers, data or values for each year.
            Dates must be ISO-8601 (YYYY-MM-DD) format. Convert if the source uses another format.
            </instructions>
            """)
        ),
        ('human', 
        """
        <context>
        {rag_context}
        </context>
        <user_query>
        {user_query}
        </user_query>
        """
        )
    ])

    chain = expenditure_agent_prompt | llm
    result = chain.invoke({
        'user_query': query,
        'rag_context': rag_context
    })

    return result


def llm_answer_writer(llm, query, revenue_answer, expenditure_answer):
    answer_writer_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=(
            """
            <instructions>
            You are the final writer in a multi-agent government finance system.
            You are given findings from up to two specialised agents - a Revenue Agent and an Expenditure Agent.
            
            Procedure:
            1. Reason inside <thinking>. List facts that are stated in the findings. Quote them.
            2. If the context does not contain enough information to answer, say so explicitly instead of guessing.
            3. Synthesize the findings into a single coherent answer to the <user_query>, cite the source and page number for each claim, and the table name if available.      
            4. Put the answer inside <answer>.

            Rules:
            If only one agent's findings are present, base your answer on that agent alone.
            If both are present, combine them into one answer and reconcile any overlap.
            Preserve figures exactly as reported by the agents; do not recalculate or round.
            Dates must be ISO-8601 (YYYY-MM-DD) format. Convert if the source uses another format.
            If neither agent found sufficient information, say so plainly.
            </instructions>
            """)
            ),
            ('human', 
            """
            <context>
            Revenue Agent Findings:\n
            {revenue_answer}
            \n\n
            Expenditure Agent Findings:\n
            {expenditure_answer}
            </context>
            <user_query>
            {user_query}
            </user_query>
            """
            )
    ])

    chain = answer_writer_prompt | llm
    result = chain.invoke({
        'user_query': query,
        'revenue_answer': revenue_answer,
        'expenditure_answer': expenditure_answer,
    })

    return result



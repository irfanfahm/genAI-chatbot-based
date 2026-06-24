from duckdb import sql
from app.llm.client import llm

def composer_node(state):

    question = state.get("question", "")

    sql_result = state.get("data", [])   # ini list of dict
    sql_query = state.get("sql", "")

    rag_context = state.get("rag_context", "")
    rag_answer = state.get("rag_answer", "")

    prompt = f"""
You are a senior BI analyst.

Question:
{question}

SQL Query:
{sql_query}

SQL Result Sample:
{sql_result[:10]}

RAG Context:
{rag_context}

RAG Answer:
{rag_answer}

Instructions:
- Answer as a business analyst.
- Combine findings from SQL and RAG.
- Write naturally as if talking to an executive.
- Do NOT use sections.
- Do NOT use bullet points.
- Do NOT use labels like Answer, Insight, Recommendation.
- answer in bahasa indonesia
- Return only one concise paragraph.
"""

    final = llm(prompt)

    return {
        **state,
        "final_answer": final
    }
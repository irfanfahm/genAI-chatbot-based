from app.llm.client import llm
from app.rag.retriever import search

def rag_node(state):

    question = state.get("question", "")

    context = search(question)

    prompt = f"""
Answer based on context:

Context:
{context}

Question:
{question}
"""

    answer = llm(prompt)

    return {
        **state,
        "rag_context": context,
        "rag_answer": answer
    }
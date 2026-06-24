from app.llm.client import llm

def router_node(state):

    question = state.get("question", "")

    prompt = f"""
You are a classification system.

Classify the question into ONLY ONE of these labels:

- sql
- rag
- hybrid

IMPORTANT:
Return ONLY the label.
No explanation.
No sentence.
No punctuation.

Question:
{question}
"""

    route = llm(prompt).strip().lower()

    # 🔥 SAFETY GUARD (INI PENTING)
    if route not in ["sql", "rag", "hybrid"]:
        route = "hybrid"

    return {
        **state,
        "route": route
    }
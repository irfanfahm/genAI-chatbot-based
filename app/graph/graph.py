from langgraph.graph import StateGraph, END

from app.nodes.router import router_node
from app.nodes.sql_node import sql_node
from app.nodes.rag_node import rag_node
from app.nodes.hybrid_node import hybrid_node
from app.nodes.composer_node import composer_node


# 1. INIT GRAPH
builder = StateGraph(dict)


# 2. ADD NODES
builder.add_node("router", router_node)
builder.add_node("sql", sql_node)
builder.add_node("rag", rag_node)
builder.add_node("hybrid", hybrid_node)
builder.add_node("composer", composer_node)


# 3. ENTRY POINT
builder.set_entry_point("router")


# 4. ROUTE FUNCTION (INI UNTUK CONDITIONAL EDGE)
def route_decision(state):
    return state["route"]   # hasil dari router_node


# 5. CONDITIONAL EDGE (INI YANG KAMU TANYA)
builder.add_conditional_edges(
    "router",
    route_decision,
    {
        "sql": "sql",
        "rag": "rag",
        "hybrid": "hybrid"
    }
)


# 6. NORMAL FLOW AFTER NODE
builder.add_edge("sql", "composer")
builder.add_edge("rag", "composer")
builder.add_edge("hybrid", "composer")

builder.add_edge("composer", END)


# 7. COMPILE
app = builder.compile()
from app.nodes.sql_node import sql_node
from app.nodes.rag_node import rag_node

def hybrid_node(state):

    state = sql_node(state)
    state = rag_node(state)

    return state
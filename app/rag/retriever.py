from  langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=emb
)

def search(query):
    docs = db.similarity_search(query, k=3)
    return "\n".join([d.page_content for d in docs])
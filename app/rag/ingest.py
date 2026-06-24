from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores  import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

loader = DirectoryLoader("docs")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(docs)

emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db = Chroma.from_documents(
    chunks,
    emb,
    persist_directory="chroma_db"
)

print("RAG indexed")
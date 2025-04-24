from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from utils import load_faiss_index, load_metadata

def load_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index = load_faiss_index()
    metadata = load_metadata()
    return FAISS(embedding_function=embeddings, index=index, documents=metadata)

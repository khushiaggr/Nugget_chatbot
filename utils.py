import pickle
import faiss

def load_faiss_index(index_path="restaurant_index.faiss"):
    return faiss.read_index(index_path)

def load_metadata(metadata_path="restaurant_metadata.pkl"):
    with open(metadata_path, "rb") as f:
        return pickle.load(f)

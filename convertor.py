import json
import faiss
import numpy as np
import pickle
from transformers import AutoTokenizer, AutoModel
import torch

# Load the model and tokenizer from Hugging Face
model_name = 'sentence-transformers/all-MiniLM-L6-v2'  # You can also use another model like 'distilbert-base-nli-stsb-mean-tokens'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embeddings(texts):
    """
    Function to get embeddings for a list of texts.
    
    Parameters:
    texts (list of str): A list of text strings for which embeddings are needed.

    Returns:
    numpy.ndarray: A NumPy array containing the embeddings for each input text.
    """
    inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state.mean(dim=1)
    return embeddings.numpy()

# === Load your scraped JSON data from 'zomato_restaurants.json' ===
with open('zomato_restaurants.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

docs = []
metadata = []

# === Extract and format text for embeddings ===
for restaurant in data:
    text = f"Name: {restaurant.get('name', '')}\n"
    text += f"URL: {restaurant.get('url', '')}\n"
    text += f"Contact: {restaurant.get('contact', 'N/A')}\n"
    text += f"Rating: {restaurant.get('rating', 'N/A')}\n"
    
    # Add menu details if available
    if 'menu' in restaurant and restaurant['menu']:
        for item in restaurant['menu']:
            text += f"Item: {item.get('name', '')}, Description: {item.get('description', '')}, Price: {item.get('price', '')}\n"
    else:
        text += "Menu: No items listed.\n"

    docs.append(text)
    metadata.append(restaurant)

# === Create embeddings ===
print("Generating embeddings in batches...")

# Batch processing for embeddings (to avoid memory issues)
def get_embeddings_in_batches(docs, batch_size=32):
    embeddings = []
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i+batch_size]
        embeddings_batch = get_embeddings(batch)
        embeddings.extend(embeddings_batch)
    return embeddings

embeddings = get_embeddings_in_batches(docs)

if len(embeddings) == 0:
    raise ValueError("No embeddings generated. Please check your documents.")

embedding_matrix = np.asarray(embeddings).astype("float32")
dimension = embedding_matrix.shape[1]

# === Build FAISS index ===
print("Building FAISS index...")
index = faiss.IndexFlatL2(dimension)
index.add(embedding_matrix)

# === Save FAISS index and metadata ===
print("Saving FAISS index and metadata...")
faiss.write_index(index, 'restaurant_index.faiss')

with open('restaurant_metadata.pkl', 'wb') as f:
    pickle.dump(metadata, f)

print("✅ Vector DB created and saved successfully.")

!pip install sentence-transformers
!pip install pinecone-client
!pip install tenserflow

import pinecone
from sentence_transformers import SentenceTransformer
import json
import pandas as pd
import numpy as np

# Initialize Pinecone
PINECONE_API_KEY = "your-pinecone-api-key"
pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY, environment='us-west1-gcp')

# Connect to the existing index
index_name = "your-index-name"
index = pinecone_client.Index(index_name)

# Define weights for each column (0 to 1)
weights = {
    "recipe_name": 0.8,
    "cuisine": 0.8,
    "ingredients": 0.8,
    "prep_time": 0.5,
    "mood_tags": 1,
    "time_tags": 0.7,
    "season_tags": 0.8,
    "description": 0.5,
}

# Function to concatenate relevant columns into a single weighted text field
def concatenate_weighted_text(row):
    weighted_text = ""
    for col, weight in weights.items():
        text = str(row[col]) if pd.notna(row[col]) else ''
        weighted_text += (text + ' ') * int(weight * 10)  # Multiply the text based on the weight
    return weighted_text.strip()

# Create a combined weighted text field for embedding
df['combined_weighted_text'] = df.apply(concatenate_weighted_text, axis=1)

# Initialize the sentence transformer model
model = SentenceTransformer('all-MPNet-base-v2')

# Encode the text to get embeddings
embeddings = model.encode(df['combined_weighted_text'].tolist())

# Prepare the data for upsert
vector_data = []
for i, embedding in enumerate(embeddings):
    # Handle potential NaN values
    recipe_name = df['recipe_name'][i] if pd.notna(df['recipe_name'][i]) else ''
    cuisine = df['cuisine'][i] if pd.notna(df['cuisine'][i]) else ''
    ingredients = df['ingredients'][i] if pd.notna(df['ingredients'][i]) else ''
    prep_time = df['prep_time'][i] if pd.notna(df['prep_time'][i]) else ''
    mood_tags = df['mood_tags'][i] if pd.notna(df['mood_tags'][i]) else ''
    time_tags = df['time_tags'][i] if pd.notna(df['time_tags'][i]) else ''
    season_tags = json.dumps(df['season_tags'][i]) if pd.notna(df['season_tags'][i]) else ''
    description = json.dumps(df['description'][i]) if pd.notna(df['description'][i]) else ''

    metadata = {
        "recipe_name": recipe_name,
        "cuisine": cuisine,
        "ingredients": ingredients,
        "prep_time": prep_time,
        "mood_tags": mood_tags,
        "time_tags": time_tags,
        "season_tags": season_tags,
        "description": description
    }

    vector_data.append((str(i), embedding.tolist(), metadata))

    # Print the metadata to debug
    print(f"Metadata for index {i}: {metadata}")

# Upsert the data in batches
batch_size = 100
for i in range(0, len(vector_data), batch_size):
    batch = vector_data[i:i+batch_size]
    index.upsert(vectors=batch)

print("Recipe data uploaded to Pinecone successfully!")


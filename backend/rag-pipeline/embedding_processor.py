import pinecone
from typing import List
from transformers import AutoTokenizer, AutoModel
import torch
import os
from chunk_processor import ChunkMetadata
from pinecone import ServerlessSpec

class ChunkVector:
    def __init__(self, metadata: ChunkMetadata, values: List[float]):
        self.metadata = metadata
        self.values = values

    def model_dump(self):
        return {
            "metadata": self.metadata.to_dict(),
            "values": self.values,
            "id": f"{self.metadata.order}_{self.metadata.source_url}",
        }

def load_finbert_model():
    model_name = "yiyanghkust/finbert-tone"  # Pre-trained FinBERT model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    return tokenizer, model

def generate_finbert_embeddings(chunk_objects: List[ChunkMetadata], tokenizer, model) -> List[ChunkVector]:
    chunk_vectors = []
    
    for chunk in chunk_objects:
        # Tokenize and create embeddings
        inputs = tokenizer(chunk.text, return_tensors="pt", max_length=512, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
            # Use the mean pooling of the last hidden state as the embedding
            embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
        
        chunk_vectors.append(
            ChunkVector(
                metadata=chunk,
                values=embeddings,
            )
        )
    return chunk_vectors

def upsert_embeddings_to_pinecone(chunk_vectors: List[ChunkVector], pinecone_api_key: str, index_name: str, namespace: str = "default"):
    # Initialize Pinecone client
    pc = pinecone.Pinecone(api_key = os.environ.get("PINECONE_API_KEY"))
    
    # Check if the index exists, and create it if it doesn’t
    if index_name not in pc.list_indexes():
        pc.create_index(
            name=index_name,
            dimension=len(chunk_vectors[0].values),  # Ensure this matches your embedding size
            metric="cosine",  # or "dotproduct" if preferred
            spec=ServerlessSpec(cloud='aws', region='us-east-1')  # specify the cloud and region
        )
    
    index = pc.Index(index_name)
    
    # Convert ChunkVector objects to dictionaries for upsertion
    encoded_chunk_vectors = [chunk.model_dump() for chunk in chunk_vectors]

    # Upsert vectors into Pinecone
    index.upsert(
        vectors=encoded_chunk_vectors,
        namespace=namespace,
    )
    print("Pinecone index updated with new embeddings")
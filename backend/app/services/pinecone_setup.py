from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from transformers import AutoTokenizer, AutoModel
import torch
import time
import os

# Initialize a Pinecone client with your API key
pc = Pinecone(os.environ.get("PINECONE_API_KEY"))

index_name = 'financial-embeddings'
dimension = 768

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
        ) 
    ) 

while not pc.describe_index(index_name).status['ready']:
    time.sleep(1)

# Connect to the index
index = pc.get_index(index_name)

# Initialize FinBERT for embedding generation
class EmbeddingGenerator:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
        self.model = AutoModel.from_pretrained("yiyanghkust/finbert-tone")

    def generate_embedding(self, text: str) -> list:
        """
        Generate an embedding for the given text using FinBERT.
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
        return embedding.tolist()

embedding_generator = EmbeddingGenerator()
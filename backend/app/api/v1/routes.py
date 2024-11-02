from app.services.embedding_generator import EmbeddingGenerator
from fastapi import APIRouter
from pydantic import BaseModel
import torch

router = APIRouter()
embedding_generator = EmbeddingGenerator()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    embedding: list

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    embedding = embedding_generator.generate_embedding(request.query)
    embedding_list = embedding.tolist()
    return QueryResponse(embedding=embedding_list)
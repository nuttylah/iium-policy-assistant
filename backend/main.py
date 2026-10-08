from fastapi import FastAPI
from pydantic import BaseModel

from backend.rag.retriever import retrieve
from backend.rag.reranker import rerank
from backend.rag.metadata_filter import (
    extract_query_constraints,
    metadata_aware_rank
)

app = FastAPI(
    title="IIUM Policy Assistant",
    description="RAG-based AI assistant for IIUM policies and regulations",
    version="1.0.0"
)


class SearchRequest(BaseModel):
    query: str


@app.get("/")
def home():
    return {
        "message": "IIUM Policy Assistant API is running!"
    }


@app.post("/search")
def search(request: SearchRequest):

    # Step 1: Retrieve Top-10 candidates using FAISS
    faiss_results = retrieve(request.query, top_k=10)

    # Step 2: Rerank candidates using Cross-Encoder
    reranked_results = rerank(
        request.query,
        faiss_results,
        top_k=10
    )

    # Step 3: Apply metadata-aware ranking
    constraints = extract_query_constraints(request.query)

    final_results = metadata_aware_rank(
        reranked_results,
        constraints
    )

    return {
        "query": request.query,
        "constraints": constraints,
        "results": final_results
    }
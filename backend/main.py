
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from backend.database import (
    save_search_history,
    get_search_history,
    get_search_history_by_id,
)

from backend.rag.retriever import retrieve
from backend.rag.reranker import rerank
from backend.rag.metadata_filter import (
    extract_query_constraints,
    metadata_aware_rank,
)
from backend.rag.generator import generate_answer


app = FastAPI(
    title="IIUM Policy Assistant",
    description="RAG-based AI assistant for IIUM policies and regulations",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

@app.get("/")
def home():
    return {
        "message": "IIUM Policy Assistant API is running!"
    }

def get_relevant_results(query: str):
    constraints = extract_query_constraints(query)

    # Retrieve a wider candidate pool.
    faiss_results = retrieve(query, top_k=50)

    if not faiss_results:
        return [], constraints

    # Apply explicit nationality and study-level constraints
    # before cross-encoder reranking.
    candidate_results = metadata_aware_rank(
        faiss_results,
        {
            **constraints,
            "intent": None,
            "condition": None,
        },
    )

    if not candidate_results:
        return [], constraints

    # Rerank only candidates matching explicit constraints.
    reranked_results = rerank(
        query,
        candidate_results,
        top_k=10,
    )

    # Apply complete metadata and policy-intent ranking.
    final_results = metadata_aware_rank(
        reranked_results,
        constraints,
    )

    return final_results, constraints

@app.post("/search")
def search(request: SearchRequest):
    """Return relevant evidence chunks without generating an answer."""

    try:
        results, constraints = get_relevant_results(request.query)

        return {
            "query": request.query,
            "constraints": constraints,
            "results": results,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(error)}",
        ) from error


@app.post("/ask")
def ask(request: SearchRequest):
    """Generate an answer using retrieved IIUM policy evidence."""

    try:
        results, constraints = get_relevant_results(request.query)

        if not results:
            answer = (
                "I could not find relevant information in the "
                "available IIUM policy documents. Please consult "
                "the relevant IIUM office."
            )

            save_search_history(request.query, answer)

            return {
                "query": request.query,
                "answer": answer,
                "constraints": constraints,
                "sources": [],
            }

        # Use the top three ranked chunks as evidence.
        evidence = results[:3]

        # Generate a grounded answer with Qwen2.5 via Ollama.
        answer = generate_answer(
            request.query,
            evidence,
        )

        # Return source information for traceability.
        sources = [
            {
                "source": result.get("metadata", {}).get("source"),
                "page": result.get("metadata", {}).get("page"),
            }
            for result in evidence
        ]

        # Save the question and answer to Supabase.
        save_search_history(request.query, answer)

        return {
            "query": request.query,
            "answer": answer,
            "constraints": constraints,
            "sources": sources,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Answer generation failed: {str(error)}",
        ) from error

@app.get("/history")
def history(
    limit: int = Query(default=20, ge=1, le=100),
):
    """Return the most recent saved questions and answers."""

    try:
        records = get_search_history(limit)

        return {
            "history": records,
            "count": len(records),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve search history: {str(error)}",
        ) from error


@app.get("/history/{history_id}")
def history_detail(history_id: int):
    """Retrieve one saved question and answer by its ID."""

    try:
        record = get_search_history_by_id(history_id)

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Search history record not found.",
            )

        return {
            "history": record
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve search history record: {str(error)}",
        ) from error

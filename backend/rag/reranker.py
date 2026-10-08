from sentence_transformers import CrossEncoder


# Cross-encoder model
MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


print(f"Loading reranker model: {MODEL_NAME}")

reranker = CrossEncoder(MODEL_NAME)


def rerank(query: str, results: list[dict], top_k: int = 4):
    """
    Re-rank retrieved chunks using a cross-encoder.
    """

    if not results:
        return []

    pairs = [
        (query, result["text"])
        for result in results
    ]

    scores = reranker.predict(pairs)

    reranked_results = []

    for result, score in zip(results, scores):
        updated_result = result.copy()
        updated_result["rerank_score"] = float(score)

        reranked_results.append(updated_result)

    reranked_results.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return reranked_results[:top_k]
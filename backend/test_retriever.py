from rag.retriever import retrieve
from rag.reranker import rerank
from rag.metadata_filter import (
    extract_query_constraints,
    metadata_aware_rank
)


questions = [
    "How long is the Malaysian Medicine undergraduate programme?",
    "What percentage of the fees is refunded if a Malaysian undergraduate withdraws during the first month?"
]


for question_number, query in enumerate(questions, start=1):

    print("\n")
    print("=" * 80)
    print(f"QUESTION {question_number}")
    print("=" * 80)
    print(query)

    # Step 1: Retrieve Top-20 candidates using FAISS
    faiss_results = retrieve(query, top_k=50)

    # Step 2: Rerank Top-20 candidates using Cross-Encoder
    reranked_results = rerank(
        query,
        faiss_results,
        top_k=50
    )

    # Step 3: Extract query constraints
    constraints = extract_query_constraints(query)

    print("\nQUERY CONSTRAINTS")
    print("-" * 70)
    print(f"Nationality : {constraints['nationality']}")
    print(f"Level       : {constraints['level']}")
    print(f"Kulliyyah   : {constraints['kulliyyah']}")

    # Step 4: Apply metadata-aware ranking
    final_results = metadata_aware_rank(
        reranked_results,
        constraints
    )

    print("\nFINAL TOP 10 RESULTS")
    print("=" * 80)

    for i, result in enumerate(final_results[:10], start=1):

        metadata = result["metadata"]

        print(f"\nRESULT {i}")
        print("-" * 70)

        print(f"Source   : {metadata['source']}")
        print(f"Page     : {metadata['page']}")
        print(f"Chunk    : {metadata['chunk']}")
        print(f"Metadata : {result['metadata_match_score']}")
        print(f"Rerank   : {result['rerank_score']:.4f}")

        print("\nText:")
        print(result["text"][:500])
        print("...")
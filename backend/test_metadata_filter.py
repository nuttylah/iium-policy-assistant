from rag.retriever import retrieve
from rag.reranker import rerank
from rag.metadata_filter import (
    extract_query_constraints,
    metadata_aware_rank
)


questions = [
    "How much is the tuition fee for Malaysian undergraduate students?",
    "How much is the tuition fee for international undergraduate students?",
    "What is the total fee for Malaysian master's students?",
    "What is the total fee for international master's students?",
    "How many semesters is the undergraduate programme?",
    "What is the entrance fee for Malaysian undergraduate students?",

    # Kulliyyah-specific questions
    "What is the total fee for international KICT undergraduate students?",
    "What is the total fee for Malaysian KICT undergraduate students?",
    "What is the total fee for international KOP undergraduate students?",
    "What is the total fee for Malaysian KOE undergraduate students?"
]


for question_number, query in enumerate(questions, start=1):

    print("\n" + "=" * 100)
    print(f"QUESTION {question_number}")
    print("=" * 100)
    print(f"Query: {query}")

    # Step 1: Extract query constraints
    constraints = extract_query_constraints(query)

    print("\nQUERY CONSTRAINTS")
    print("-" * 100)

    for key, value in constraints.items():
        print(f"{key.capitalize():<15}: {value}")

    # Step 2: Retrieve candidates using FAISS
    results = retrieve(query, top_k=30)

    print(f"\nFAISS candidates retrieved: {len(results)}")

    # Step 3: Rerank candidates using Cross-Encoder
    reranked_results = rerank(
        query,
        results,
        top_k=30
    )

    print(f"Candidates after reranking: {len(reranked_results)}")

    # Step 4: Apply metadata filtering and ranking
    final_results = metadata_aware_rank(
        reranked_results,
        constraints
    )

    print(f"Results after metadata filtering: {len(final_results)}")

    print("\nFINAL METADATA-AWARE RANKING")
    print("-" * 100)

    if not final_results:
        print(
            "No results match all explicit metadata constraints. "
            "Check the retrieved candidates, metadata, or increase top_k."
        )
        continue

    for rank, result in enumerate(final_results[:4], start=1):

        metadata = result["metadata"]

        print(f"\nRank {rank}")
        print(f"Source          : {metadata.get('source', 'Unknown')}")
        print(f"Page            : {metadata.get('page', 'Unknown')}")
        print(f"Nationality     : {metadata.get('nationality', 'Unknown')}")
        print(f"Level           : {metadata.get('level', 'Unknown')}")
        print(f"Kulliyyah       : {metadata.get('kulliyyah', 'Unknown')}")
        print(
            f"Metadata score  : "
            f"{result.get('metadata_match_score', 0)}"
        )
        print(
            f"Rerank score    : "
            f"{result.get('rerank_score', 0.0):.4f}"
        )
        print(f"Text preview     : {result['text'][:500]}")
        print("-" * 60)

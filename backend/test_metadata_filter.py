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

    print("\n" + "=" * 80)
    print(f"QUESTION {question_number}")
    print("=" * 80)
    print(query)

    # Extract query constraints
    constraints = extract_query_constraints(query)

    print("\nQUERY CONSTRAINTS")
    print("-" * 80)
    print(f"Nationality : {constraints['nationality']}")
    print(f"Level       : {constraints['level']}")
    print(f"Kulliyyah   : {constraints['kulliyyah']}")

    # Retrieve Top 10 using FAISS
    results = retrieve(query, top_k=10)

    # Rerank Top 10
    reranked_results = rerank(
        query,
        results,
        top_k=10
    )

    # Apply metadata-aware ranking
    final_results = metadata_aware_rank(
        reranked_results,
        constraints
    )

    print("\nFINAL METADATA-AWARE RANKING")
    print("-" * 80)

    for i, result in enumerate(final_results[:4], start=1):

        metadata = result["metadata"]

        print(
            f"{i}. "
            f"{metadata['source']} | "
            f"Page {metadata['page']} | "
            f"Nationality: {metadata['nationality']} | "
            f"Level: {metadata['level']} | "
            f"Kulliyyah: {metadata['kulliyyah']} | "
            f"Metadata: {result['metadata_match_score']} | "
            f"Rerank: {result['rerank_score']:.4f}"
        )
from rag.retriever import retrieve
from rag.reranker import rerank


questions = [
    "How much is the tuition fee for Malaysian undergraduate students?",
    "How much is the tuition fee for international undergraduate students?",
    "What is the total fee for Malaysian master's students?",
    "What is the total fee for international master's students?",
    "How many semesters is the undergraduate programme?",
    "What is the entrance fee for Malaysian undergraduate students?"
]


for question_number, query in enumerate(questions, start=1):

    print("\n" + "=" * 80)
    print(f"QUESTION {question_number}")
    print("=" * 80)
    print(query)

    # Retrieve top 10 using FAISS
    results = retrieve(query, top_k=10)

    print("\n" + "-" * 80)
    print("BEFORE RERANKING (FAISS Top 10)")
    print("-" * 80)

    for i, result in enumerate(results, start=1):
        print(
            f"{i}. "
            f"{result['metadata']['source']} | "
            f"Page {result['metadata']['page']} | "
            f"FAISS Score: {result['score']:.4f}"
        )

    # Rerank the top 10 results
    reranked_results = rerank(
        query,
        results,
        top_k=4
    )

    print("\n" + "-" * 80)
    print("AFTER RERANKING (Top 4)")
    print("-" * 80)

    for i, result in enumerate(reranked_results, start=1):
        print(
            f"{i}. "
            f"{result['metadata']['source']} | "
            f"Page {result['metadata']['page']} | "
            f"Rerank Score: {result['rerank_score']:.4f}"
        )
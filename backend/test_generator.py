
from rag.retriever import retrieve
from rag.reranker import rerank
from rag.metadata_filter import (
    extract_query_constraints,
    metadata_aware_rank,
)
from rag.generator import generate_answer


def main():
    question = (
        "What percentage of the fees is refunded if a Malaysian "
        "undergraduate withdraws during the first month?"
    )

    print("=" * 70)
    print("QUESTION")
    print("=" * 70)
    print(question)

    # 1. Retrieve relevant document chunks.
    results = retrieve(question, top_k=50)

    # 2. Rerank the retrieved chunks.
    results = rerank(question, results, top_k=50)

    # 3. Apply metadata filtering and ranking.
    constraints = extract_query_constraints(question)
    results = metadata_aware_rank(results, constraints)

    if not results:
        print("\nNo relevant evidence was found.")
        return

    # 4. Use the top three chunks as evidence for the LLM.
    evidence = results[:3]

    print("\n" + "=" * 70)
    print("GENERATED ANSWER")
    print("=" * 70)

    answer = generate_answer(question, evidence)
    print(answer)


if __name__ == "__main__":
    main()

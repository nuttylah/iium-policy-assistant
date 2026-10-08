from rag.retriever import retrieve
from rag.reranker import rerank


QUESTIONS = [
    "How much is the entrance fee for Malaysian Pharmacy students?",
    "What is the total fee for Malaysian Pharmacy undergraduate students?",
    "How long is the Malaysian Medicine undergraduate programme?",
    "What is the total fee for Malaysian Dentistry students?",
    "What is the total fee for Malaysian Nursing ODL students?",
    "What is the total fee for Malaysian Pre-Sessional CELPAD students?",
    "What percentage of the fees is refunded if a Malaysian undergraduate withdraws during the first month?",
    "What is the entrance fee for international KOP undergraduate students?",
    "What is the total cost for an international KOP undergraduate programme?",
    "What is the total fee for international Medicine undergraduate students?",
    "How much is the total fee for international Dentistry students?",
    "What is the total fee for international Nursing ODL students?"
]


for query in QUESTIONS:

    print("\n" + "=" * 100)
    print("QUESTION:")
    print(query)
    print("=" * 100)

    results = retrieve(query, top_k=4)

    print("\n--- FAISS TOP 4 ---")

    for rank, result in enumerate(results, start=1):

        metadata = result["metadata"]

        print(f"\nRank {rank}")
        print(f"Score: {result['score']}")
        print(f"Source: {metadata['source']}")
        print(f"Page: {metadata['page']}")
        print(f"Chunk: {metadata['chunk']}")
        print(f"Nationality: {metadata['nationality']}")
        print(f"Level: {metadata['level']}")

        print("\nText preview:")
        print(result["text"][:500])

    reranked = rerank(
        query,
        results,
        top_k=4
    )

    print("\n--- CROSS-ENCODER TOP 4 ---")

    for rank, result in enumerate(reranked, start=1):

        metadata = result["metadata"]

        print(f"\nRank {rank}")
        print(f"Rerank score: {result['rerank_score']}")
        print(f"Source: {metadata['source']}")
        print(f"Page: {metadata['page']}")
        print(f"Chunk: {metadata['chunk']}")

        print("\nText preview:")
        print(result["text"][:500])
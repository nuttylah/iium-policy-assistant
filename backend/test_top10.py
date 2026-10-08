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


EXPECTED = {
    "How much is the entrance fee for Malaysian Pharmacy students?": (
        "IIUM_TUITION FEES UNDERGRADUATED.pdf", 14, 1
    ),

    "What is the total fee for Malaysian Pharmacy undergraduate students?": (
        "IIUM_TUITION FEES UNDERGRADUATED.pdf", 14, 1
    ),

    "How long is the Malaysian Medicine undergraduate programme?": (
        "IIUM_TUITION FEES UNDERGRADUATED.pdf", 15, 1
    ),

    "What is the total fee for Malaysian Dentistry students?": (
        "IIUM_TUITION FEES UNDERGRADUATED.pdf", 16, 1
    ),

    "What is the total fee for Malaysian Nursing ODL students?": (
        "IIUM_TUITION FEES UNDERGRADUATED.pdf", 18, 1
    ),

    "What is the total fee for Malaysian Pre-Sessional CELPAD students?": (
        "IIUM_TUITION FEES UNDERGRADUATED.pdf", 19, 1
    ),

    "What percentage of the fees is refunded if a Malaysian undergraduate withdraws during the first month?": (
        "IIUM_TUITION FEES UNDERGRADUATED.pdf", 2, 1
    ),

    "What is the entrance fee for international KOP undergraduate students?": (
        "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf", 14, 1
    ),

    "What is the total cost for an international KOP undergraduate programme?": (
        "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf", 14, 1
    ),

    "What is the total fee for international Medicine undergraduate students?": (
        "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf", 15, 1
    ),

    "How much is the total fee for international Dentistry students?": (
        "IIUM_MASTER TUITION FEE INTERNATIONAL.pdf", 23, 1
    ),

    "What is the total fee for international Nursing ODL students?": (
        "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf", 18, 1
    )
}


for query in QUESTIONS:

    print("\n" + "=" * 100)
    print("QUESTION:")
    print(query)
    print("=" * 100)

    results = retrieve(query, top_k=10)

    expected_source, expected_page, expected_chunk = EXPECTED[query]

    found_rank = None

    for rank, result in enumerate(results, start=1):

        metadata = result["metadata"]

        if (
            metadata["source"] == expected_source
            and metadata["page"] == expected_page
            and metadata["chunk"] == expected_chunk
        ):
            found_rank = rank

        print(
            f"Rank {rank}: "
            f"{metadata['source']} | "
            f"Page {metadata['page']} | "
            f"Chunk {metadata['chunk']}"
        )

    print("\nCorrect chunk rank in FAISS Top 10:", found_rank)

    reranked = rerank(
        query,
        results,
        top_k=4
    )

    rerank_rank = None

    for rank, result in enumerate(reranked, start=1):

        metadata = result["metadata"]

        if (
            metadata["source"] == expected_source
            and metadata["page"] == expected_page
            and metadata["chunk"] == expected_chunk
        ):
            rerank_rank = rank

    print("Correct chunk rank after Cross Encoder:", rerank_rank)
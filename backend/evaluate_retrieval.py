from rag.retriever import retrieve
from rag.reranker import rerank
from rag.metadata_filter import (
    extract_query_constraints,
    metadata_aware_rank
)


EVALUATION_DATASET = [

    {
        "id": "Q01",
        "query": "How much is the total fee for Malaysian KICT undergraduate students?",
        "expected_answer": "RM12,860",
        "expected_source": "IIUM_TUITION FEES UNDERGRADUATED.pdf",
        "expected_page": 4,
        "expected_chunk": 1
    },

    {
        "id": "Q02",
        "query": "What is the tuition fee for Malaysian KICT undergraduate students?",
        "expected_answer": "RM4,400",
        "expected_source": "IIUM_TUITION FEES UNDERGRADUATED.pdf",
        "expected_page": 4,
        "expected_chunk": 1
    },

    {
        "id": "Q03",
        "query": "How much is the entrance fee for Malaysian Pharmacy students?",
        "expected_answer": "RM710",
        "expected_source": "IIUM_TUITION FEES UNDERGRADUATED.pdf",
        "expected_page": 14,
        "expected_chunk": 1
    },

    {
        "id": "Q04",
        "query": "What is the total fee for Malaysian Pharmacy undergraduate students?",
        "expected_answer": "RM20,040",
        "expected_source": "IIUM_TUITION FEES UNDERGRADUATED.pdf",
        "expected_page": 14,
        "expected_chunk": 1
    },

    {
        "id": "Q05",
        "query": "How long is the Malaysian Medicine undergraduate programme?",
        "expected_answer": "5 years / 10 semesters",
        "expected_source": "IIUM_TUITION FEES UNDERGRADUATED.pdf",
        "expected_page": 15,
        "expected_chunk": 1
    },

    {
        "id": "Q06",
        "query": "What is the total fee for Malaysian Dentistry students?",
        "expected_answer": "RM24,015",
        "expected_source": "IIUM_TUITION FEES UNDERGRADUATED.pdf",
        "expected_page": 16,
        "expected_chunk": 1
    },

    {
        "id": "Q07",
        "query": "What is the total fee for Malaysian Nursing ODL students?",
        "expected_answer": "RM25,000",
        "expected_source": "IIUM_TUITION FEES UNDERGRADUATED.pdf",
        "expected_page": 18,
        "expected_chunk": 1
    },

    {
        "id": "Q08",
        "query": "How many semesters are covered by the Malaysian Nursing ODL tuition fee?",
        "expected_answer": "6 semesters",
        "expected_source": "IIUM_TUITION FEES UNDERGRADUATED.pdf",
        "expected_page": 18,
        "expected_chunk": 1
    },

    {
        "id": "Q09",
        "query": "What is the total fee for Malaysian Pre-Sessional CELPAD students?",
        "expected_answer": "RM6,450",
        "expected_source": "IIUM_TUITION FEES UNDERGRADUATED.pdf",
        "expected_page": 19,
        "expected_chunk": 1
    },

    {
        "id": "Q10",
        "query": "What percentage of the fees is refunded if a Malaysian undergraduate withdraws during the first month?",
        "expected_answer": "90%",
        "expected_source": "IIUM_TUITION FEES UNDERGRADUATED.pdf",
        "expected_page": 2,
        "expected_chunk": 1
    },

    {
        "id": "Q11",
        "query": "What is the total fee for international KICT undergraduate students?",
        "expected_answer": "RM81,265",
        "expected_source": "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf",
        "expected_page": 4,
        "expected_chunk": 1
    },

    {
        "id": "Q12",
        "query": "How much is the tuition fee for an international KICT undergraduate student?",
        "expected_answer": "RM57,600",
        "expected_source": "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf",
        "expected_page": 4,
        "expected_chunk": 1
    },

    {
        "id": "Q13",
        "query": "What is the entrance fee for international KOP undergraduate students?",
        "expected_answer": "RM1,585",
        "expected_source": "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf",
        "expected_page": 14,
        "expected_chunk": 1
    },

    {
        "id": "Q14",
        "query": "What is the total cost for an international KOP undergraduate programme?",
        "expected_answer": "RM169,785",
        "expected_source": "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf",
        "expected_page": 14,
        "expected_chunk": 1
    },

    {
        "id": "Q15",
        "query": "How many semesters does the international KOE undergraduate programme have?",
        "expected_answer": "8 semesters",
        "expected_source": "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf",
        "expected_page": 9,
        "expected_chunk": 1
    },

    {
        "id": "Q16",
        "query": "What is the total fee for international Medicine undergraduate students?",
        "expected_answer": "RM383,940",
        "expected_source": "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf",
        "expected_page": 15,
        "expected_chunk": 1
    },

    {
        "id": "Q17",
        "query": "How much is the total fee for international Dentistry students?",
        "expected_answer": "RM387,540",
        "expected_source": "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf",
        "expected_page": 16,
        "expected_chunk": 1
    },

    {
        "id": "Q18",
        "query": "What is the total fee for international Nursing ODL students?",
        "expected_answer": "RM45,265",
        "expected_source": "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf",
        "expected_page": 18,
        "expected_chunk": 1
    },

    {
        "id": "Q19",
        "query": "Is the entrance fee refundable for international undergraduate students?",
        "expected_answer": "No, it is non-refundable",
        "expected_source": "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf",
        "expected_page": 2,
        "expected_chunk": 1
    },

    {
        "id": "Q20",
        "query": "When did SST start applying to taxable fees for international students?",
        "expected_answer": "1 July 2025",
        "expected_source": "IIUM_TUITION FEES INTERNATIONAL UNDERGRADUATED.pdf",
        "expected_page": 2,
        "expected_chunk": 1
    },

    {
        "id": "Q21",
        "query": "What is the total fee for the Malaysian Master of Protective Security Management programme full-time?",
        "expected_answer": "RM21,690",
        "expected_source": "IIUM_MASTER TUITION FEE MALAYSIAN.pdf",
        "expected_page": 6,
        "expected_chunk": 1
    },

    {
        "id": "Q22",
        "query": "How much does the Malaysian Master of Business Intelligence and Analytic programme cost full-time?",
        "expected_answer": "RM19,690",
        "expected_source": "IIUM_MASTER TUITION FEE MALAYSIAN.pdf",
        "expected_page": 8,
        "expected_chunk": 1
    },

    {
        "id": "Q23",
        "query": "What is the total fee for the Malaysian Master of Architecture programme part-time?",
        "expected_answer": "RM18,610",
        "expected_source": "IIUM_MASTER TUITION FEE MALAYSIAN.pdf",
        "expected_page": 27,
        "expected_chunk": 1
    },

    {
        "id": "Q24",
        "query": "How much is the total fee for Malaysian Master of Cosmetic Science in mixed mode?",
        "expected_answer": "RM23,890",
        "expected_source": "IIUM_MASTER TUITION FEE MALAYSIAN.pdf",
        "expected_page": 34,
        "expected_chunk": 1
    },

    {
        "id": "Q25",
        "query": "What is the total fee for Malaysian Master of Advance Nursing in mixed mode?",
        "expected_answer": "RM13,440",
        "expected_source": "IIUM_MASTER TUITION FEE MALAYSIAN.pdf",
        "expected_page": 35,
        "expected_chunk": 1
    },

    {
        "id": "Q26",
        "query": "What is the total fee for the international Master of Protective Security Management programme?",
        "expected_answer": "RM26,830",
        "expected_source": "IIUM_MASTER TUITION FEE INTERNATIONAL.pdf",
        "expected_page": 4,
        "expected_chunk": 1
    },

    {
        "id": "Q27",
        "query": "How much does the international Master of Business Intelligence and Analytic programme cost?",
        "expected_answer": "RM30,830",
        "expected_source": "IIUM_MASTER TUITION FEE INTERNATIONAL.pdf",
        "expected_page": 5,
        "expected_chunk": 1
    },

    {
        "id": "Q28",
        "query": "What is the total fee for the international Master of Dentistry programme?",
        "expected_answer": "RM105,410",
        "expected_source": "IIUM_MASTER TUITION FEE INTERNATIONAL.pdf",
        "expected_page": 23,
        "expected_chunk": 1
    },

    {
        "id": "Q29",
        "query": "What is the total fee for the international Master in Halal Industry Science programme?",
        "expected_answer": "Approximately RM35,830",
        "expected_source": "IIUM_MASTER TUITION FEE INTERNATIONAL.pdf",
        "expected_page": 29,
        "expected_chunk": 1
    },

    {
        "id": "Q30",
        "query": "What is the total fee for the international Master of Human Science Psychology (Clinical)?",
        "expected_answer": "RM46,830",
        "expected_source": "IIUM_MASTER TUITION FEE INTERNATIONAL.pdf",
        "expected_page": 10,
        "expected_chunk": 1
    }
]


def is_correct(result, evaluation_item):
    metadata = result["metadata"]

    return (
        metadata["source"] == evaluation_item["expected_source"]
        and metadata["page"] == evaluation_item["expected_page"]
        and metadata["chunk"] == evaluation_item["expected_chunk"]
    )


def evaluate():

    print("=" * 100)
    print("RAG RETRIEVAL EVALUATION")
    print("=" * 100)

    faiss_correct = 0
    reranker_correct = 0
    metadata_correct = 0

    for item in EVALUATION_DATASET:

        query = item["query"]

        print("\n" + "-" * 100)
        print(f"{item['id']}: {query}")
        print("-" * 100)

        # FAISS
        # Retrieve Top 10 candidates instead of Top 4
        faiss_results = retrieve(query, top_k=10)

        faiss_rank = None

        for rank, result in enumerate(faiss_results, start=1):
            if is_correct(result, item):
                faiss_rank = rank
                break

        if faiss_rank == 1:
            faiss_correct += 1

        # Cross-Encoder
        # Rerank the Top 10 candidates and keep Top 4
        reranked_results = rerank(
            query,
            faiss_results,
            top_k=10
        )

        reranker_rank = None

        for rank, result in enumerate(reranked_results, start=1):
            if is_correct(result, item):
                reranker_rank = rank
                break

        if reranker_rank == 1:
            reranker_correct += 1

        # Metadata
        constraints = extract_query_constraints(query)

        metadata_results = metadata_aware_rank(
            reranked_results,
            constraints
        )

        metadata_rank = None

        for rank, result in enumerate(metadata_results, start=1):
            if is_correct(result, item):
                metadata_rank = rank
                break

        if metadata_rank == 1:
            metadata_correct += 1

        print(f"FAISS correct rank       : {faiss_rank}")
        print(f"Cross-Encoder rank      : {reranker_rank}")
        print(f"Metadata-aware rank     : {metadata_rank}")

    total = len(EVALUATION_DATASET)

    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)

    print(
        f"FAISS Top-1 Accuracy                : "
        f"{faiss_correct / total * 100:.2f}%"
    )

    print(
        f"Cross-Encoder Top-1 Accuracy        : "
        f"{reranker_correct / total * 100:.2f}%"
    )

    print(
        f"Metadata-aware Top-1 Accuracy       : "
        f"{metadata_correct / total * 100:.2f}%"
    )

    print("=" * 100)


if __name__ == "__main__":
    evaluate()
    

from pathlib import Path

import pymupdf

from rag.retriever import retrieve
from rag.reranker import rerank
from rag.metadata_filter import (
    extract_query_constraints,
    metadata_aware_rank,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"

TEST_CASES = [
    {
        "name": "Medicine undergraduate duration",
        "query": "How long is the Malaysian Medicine undergraduate programme?",
        "expected_evidence": [
            "kulliyyah of medicine",
            "5 years",
        ],
    },
    {
        "name": "First-month withdrawal refund",
        "query": (
            "What percentage of the fees is refunded if a Malaysian "
            "undergraduate withdraws during the first month?"
        ),
        "expected_evidence": [
            "first month",
            "90%",
            "refund",
        ],
    },
]


def check_source_refund_policy() -> bool:
    """
    Validate the refund policy directly from the original PDF page.
    This checks source wording, not retrieval performance.
    """
    pdf_path = (
        DOCUMENTS_DIR
        / "IIUM_TUITION FEES MALAYSIAN UNDERGRADUATED.pdf"
    )

    print("\n" + "=" * 80)
    print("SOURCE REFUND POLICY VALIDATION")
    print("=" * 80)

    if not pdf_path.exists():
        print(f"FAIL: Source PDF not found: {pdf_path}")
        return False

    try:
        with pymupdf.open(pdf_path) as pdf:
            # Page 2 of the PDF, using a zero-based index.
            page_text = pdf[1].get_text("text", sort=True)

        normalized_text = " ".join(page_text.lower().split())

        expected_statements = [
            "from the first day up to the first month – 90% refund",
            "from the first month up to the second month – 60% refund",
            "after the second month of the semester – no refund",
        ]

        all_found = all(
            statement in normalized_text
            for statement in expected_statements
        )

        if all_found:
            print("PASS: All three refund statements match the source.")
            return True

        print(
            "FAIL: The expected statements were not found exactly "
            "in the extracted source text."
        )
        print("\nExtracted refund-related lines:")

        for line in page_text.splitlines():
            if any(
                term in line.lower()
                for term in ("first day", "first month", "second month", "refund")
            ):
                print(line)

        return False

    except Exception as error:
        print(f"ERROR reading source PDF: {type(error).__name__}: {error}")
        return False


def run_retrieval_test(test_case: dict) -> bool:
    query = test_case["query"]

    print("\n" + "=" * 80)
    print(test_case["name"])
    print("=" * 80)
    print("Question:", query)

    # 1. Retrieve candidates from FAISS.
    faiss_results = retrieve(query, top_k=50)
    print("FAISS candidates:", len(faiss_results))

    if not faiss_results:
        print("FAIL: FAISS returned no candidates.")
        return False

    # 2. Rerank candidates.
    reranked_results = rerank(query, faiss_results, top_k=50)
    print("Reranked candidates:", len(reranked_results))

    # 3. Apply metadata-aware ranking.
    constraints = extract_query_constraints(query)
    print("Constraints:", constraints)

    final_results = metadata_aware_rank(
        reranked_results,
        constraints,
    )

    print("Final results:", len(final_results))

    if not final_results:
        print("FAIL: Metadata filtering removed all candidates.")
        return False

    # 4. Display the top three chunks.
    for index, result in enumerate(final_results[:3], start=1):
        metadata = result["metadata"]

        print(f"\nRESULT {index}")
        print("Source:", metadata.get("source"))
        print("Page:", metadata.get("page"))
        print("Kulliyyah:", metadata.get("kulliyyah"))
        print("Metadata score:", result.get("metadata_match_score"))
        print("Reranker score:", result.get("rerank_score"))
        print("Evidence:")
        print(result["text"][:600])

    # 5. Check the expected evidence terms.
    matching_result = next(
        (
            result
            for result in final_results
            if all(
                phrase in result.get("text", "").lower()
                for phrase in test_case["expected_evidence"]
            )
        ),
        None,
    )

    if matching_result:
        print("\nPASS: A retrieved chunk contains the expected terms.")
        return True

    print("\nFAIL: No retrieved chunk contains all expected terms.")
    print("Expected evidence:", test_case["expected_evidence"])
    return False


def main():
    results = []

    # Validate the source independently of retrieval.
    source_policy_passed = check_source_refund_policy()
    results.append(("Source refund policy validation", source_policy_passed))

    # Test retrieval.
    for test_case in TEST_CASES:
        try:
            passed = run_retrieval_test(test_case)
        except Exception as error:
            print(f"\nERROR: {type(error).__name__}: {error}")
            passed = False

        results.append((test_case["name"], passed))

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for name, passed in results:
        print(f"{'PASS' if passed else 'FAIL'}: {name}")

    passed_count = sum(passed for _, passed in results)
    print(f"\nPassed: {passed_count}/{len(results)}")


if __name__ == "__main__":
    main()

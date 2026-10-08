from rag.retriever import retrieve
from rag.reranker import rerank
from rag.metadata_filter import (
    extract_query_constraints,
    metadata_aware_rank
)

query = "What percentage of the fees is refunded if a Malaysian undergraduate withdraws during the first month?"

target_source = "IIUM_TUITION FEES UNDERGRADUATED.pdf"
target_page = 2
target_chunk = 1


print("=" * 80)
print("POLICY INTENT TEST")
print("=" * 80)
print(f"Query: {query}")


# ============================================================
# STEP 1: Extract query constraints
# ============================================================

constraints = extract_query_constraints(query)

print("\nQUERY CONSTRAINTS")
print("=" * 80)

print(f"Nationality : {constraints['nationality']}")
print(f"Level       : {constraints['level']}")
print(f"Kulliyyah   : {constraints['kulliyyah']}")
print(f"Intent      : {constraints['intent']}")
print(f"Condition   : {constraints['condition']}")


# ============================================================
# STEP 2: Retrieve Top 50 using FAISS
# ============================================================

faiss_results = retrieve(query, top_k=50)


print("\nTOP 10 FAISS RESULTS")
print("=" * 80)

for rank, result in enumerate(faiss_results[:10], start=1):

    metadata = result["metadata"]

    print(
        f"Rank {rank} | "
        f"Page {metadata['page']} | "
        f"Chunk {metadata['chunk']} | "
        f"Score {result['score']:.4f}"
    )


# ============================================================
# STEP 3: Find correct chunk in FAISS
# ============================================================

for rank, result in enumerate(faiss_results, start=1):

    metadata = result["metadata"]

    if (
        metadata["source"] == target_source
        and metadata["page"] == target_page
        and metadata["chunk"] == target_chunk
    ):

        print("\nCORRECT CHUNK IN FAISS")
        print("=" * 80)

        print(f"FAISS Rank : {rank}")
        print(f"FAISS Score: {result['score']:.4f}")

        break


# ============================================================
# STEP 4: Cross Encoder
# ============================================================

reranked_results = rerank(
    query,
    faiss_results,
    top_k=50
)


print("\nTOP 10 CROSS ENCODER RESULTS")
print("=" * 80)

for rank, result in enumerate(reranked_results[:10], start=1):

    metadata = result["metadata"]

    print(
        f"Rank {rank} | "
        f"Source {metadata['source']} | "
        f"Page {metadata['page']} | "
        f"Score {result['rerank_score']:.4f}"
    )


# ============================================================
# STEP 5: Find correct chunk after Cross Encoder
# ============================================================

for rank, result in enumerate(reranked_results, start=1):

    metadata = result["metadata"]

    if (
        metadata["source"] == target_source
        and metadata["page"] == target_page
        and metadata["chunk"] == target_chunk
    ):

        print("\nCORRECT CHUNK AFTER CROSS ENCODER")
        print("=" * 80)

        print(f"Cross Encoder Rank : {rank}")
        print(f"Cross Encoder Score: {result['rerank_score']:.4f}")

        break


# ============================================================
# STEP 6: Metadata + Policy Intent Ranking
# ============================================================

final_results = metadata_aware_rank(
    reranked_results,
    constraints
)


print("\nTOP 10 AFTER METADATA + INTENT RANKING")
print("=" * 80)

for rank, result in enumerate(final_results[:10], start=1):

    metadata = result["metadata"]

    print(
        f"Rank {rank} | "
        f"Source {metadata['source']} | "
        f"Page {metadata['page']} | "
        f"Metadata Score {result['metadata_match_score']} | "
        f"CE Score {result['rerank_score']:.4f}"
    )


# ============================================================
# STEP 7: Find correct chunk after metadata + intent ranking
# ============================================================

for rank, result in enumerate(final_results, start=1):

    metadata = result["metadata"]

    if (
        metadata["source"] == target_source
        and metadata["page"] == target_page
        and metadata["chunk"] == target_chunk
    ):

        print("\nCORRECT CHUNK AFTER METADATA + INTENT")
        print("=" * 80)

        print(f"Final Rank    : {rank}")
        print(f"Metadata Score: {result['metadata_match_score']}")
        print(f"CE Score      : {result['rerank_score']:.4f}")

        break


# ============================================================
# STEP 8: Inspect top metadata-ranked chunks
# ============================================================

print("\nTOP 10 METADATA RESULTS - TEXT INSPECTION")
print("=" * 80)

for rank, result in enumerate(final_results[:10], start=1):

    metadata = result["metadata"]

    print("\n" + "-" * 80)

    print(
        f"Rank {rank} | "
        f"Source: {metadata['source']} | "
        f"Page: {metadata['page']} | "
        f"Chunk: {metadata['chunk']}"
    )

    print(
        f"Metadata Score: {result['metadata_match_score']} | "
        f"CE Score: {result['rerank_score']:.4f}"
    )

    print("\nTEXT:")
    print(result["text"])
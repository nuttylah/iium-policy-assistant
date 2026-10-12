
from pathlib import Path
import json
import re

import faiss
from sentence_transformers import SentenceTransformer


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore"
INDEX_PATH = VECTORSTORE_DIR / "index.faiss"
METADATA_PATH = VECTORSTORE_DIR / "metadata.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Cached resources
_index = None
_metadata = None
_model = None


def load_vector_store():
    """Load the FAISS index, metadata, and embedding model once."""
    global _index, _metadata, _model

    if _index is not None and _metadata is not None and _model is not None:
        return _index, _metadata, _model

    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"FAISS index not found: {INDEX_PATH}")

    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")

    print("Loading vector store...")
    _index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        _metadata = json.load(file)

    if _index.ntotal != len(_metadata):
        raise ValueError(
            f"FAISS index has {_index.ntotal} vectors, "
            f"but metadata contains {len(_metadata)} chunks."
        )

    print("Loading embedding model...")
    _model = SentenceTransformer(MODEL_NAME)

    return _index, _metadata, _model


def normalize_text(text: str) -> str:
    """Normalize text for exact duplicate detection."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w%]+", " ", text)
    return text.strip()


def retrieve(query: str, top_k: int = 4):
    """
    Retrieve the top_k most relevant chunks using FAISS.

    Results retain their original text and metadata. Exact duplicate
    chunks are removed, but similar chunks from different programmes
    are retained because their context may differ.
    """
    if not query or not query.strip():
        raise ValueError("Query must not be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    index, metadata, model = load_vector_store()

    print(f"Searching for: {query}")

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    # Retrieve a wider candidate pool to allow duplicate removal.
    candidate_k = min(index.ntotal, max(top_k * 5, top_k))

    distances, indices = index.search(
        query_embedding,
        candidate_k
    )

    results = []
    seen_texts = set()

    for distance, index_position in zip(distances[0], indices[0]):
        if index_position == -1:
            continue

        result = metadata[index_position].copy()
        normalized = normalize_text(result.get("text", ""))

        # Remove exact duplicates only.
        if not normalized or normalized in seen_texts:
            continue

        seen_texts.add(normalized)
        result["score"] = float(distance)
        results.append(result)

        if len(results) >= top_k:
            break

    return results

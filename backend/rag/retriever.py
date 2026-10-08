from pathlib import Path
import json

import faiss
from sentence_transformers import SentenceTransformer


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore"

INDEX_PATH = VECTORSTORE_DIR / "index.faiss"
METADATA_PATH = VECTORSTORE_DIR / "metadata.json"


# Same embedding model used when creating the vector store
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# Cache for loaded resources
_index = None
_metadata = None
_model = None


def load_vector_store():
    """
    Load the FAISS index, metadata, and embedding model once.
    """

    global _index, _metadata, _model

    # If already loaded, reuse them
    if _index is not None and _metadata is not None and _model is not None:
        return _index, _metadata, _model

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {INDEX_PATH}"
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {METADATA_PATH}"
        )

    print("Loading vector store...")

    _index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        _metadata = json.load(file)

    print("Loading embedding model...")

    _model = SentenceTransformer(MODEL_NAME)

    return _index, _metadata, _model


def retrieve(query: str, top_k: int = 4):
    """
    Retrieve the most relevant chunks for a user query.
    """

    index, metadata, model = load_vector_store()

    print(f"Searching for: {query}")

    # Convert question into an embedding
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    # Search FAISS
    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for distance, index_position in zip(
        distances[0],
        indices[0]
    ):

        if index_position == -1:
            continue

        result = metadata[index_position].copy()

        result["score"] = float(distance)

        results.append(result)

    return results
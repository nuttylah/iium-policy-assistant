from pathlib import Path
import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore"

INDEX_PATH = VECTORSTORE_DIR / "index.faiss"
METADATA_PATH = VECTORSTORE_DIR / "metadata.json"


# Embedding model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def create_vector_store(chunks: list[dict]):
    """
    Convert text chunks into embeddings and store them in FAISS.
    Metadata is saved separately in JSON format.
    """

    if not chunks:
        raise ValueError("No chunks provided.")

    print(f"Loading embedding model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    texts = [chunk["text"] for chunk in chunks]

    print(f"Generating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    # FAISS requires float32
    embeddings = np.asarray(embeddings, dtype="float32")

    # Get embedding dimension
    dimension = embeddings.shape[1]

    # Create FAISS index
    index = faiss.IndexFlatL2(dimension)

    # Add embeddings to FAISS
    index.add(embeddings)

    # Create vectorstore folder if needed
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

    # Save FAISS index
    faiss.write_index(index, str(INDEX_PATH))

    # Save chunk metadata
    with open(METADATA_PATH, "w", encoding="utf-8") as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\nVector store created successfully!")
    print(f"Total vectors: {index.ntotal}")
    print(f"Embedding dimension: {dimension}")
    print(f"FAISS index: {INDEX_PATH}")
    print(f"Metadata: {METADATA_PATH}")
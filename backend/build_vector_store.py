from pathlib import Path

from backend.rag.pdf_processor import process_pdf
from backend.rag.vector_store import create_vector_store

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"


def main():
    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {DOCUMENTS_DIR}"
        )

    print(f"Found {len(pdf_files)} PDF files.")

    all_chunks = []

    for pdf_path in pdf_files:
        print("\n" + "=" * 70)
        print(f"Processing: {pdf_path.name}")
        print("=" * 70)

        chunks = process_pdf(str(pdf_path))

        print(f"Chunks extracted: {len(chunks)}")

        if not chunks:
            print("WARNING: No chunks extracted from this PDF.")

        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError(
            "No chunks were extracted. Vector store was not rebuilt."
        )

    print("\n" + "=" * 70)
    print(f"Total PDFs: {len(pdf_files)}")
    print(f"Total chunks: {len(all_chunks)}")
    print("=" * 70)

    confirm = input(
        "\nThis will replace the existing FAISS index and metadata. "
        "Continue? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Cancelled. Existing vector store was not changed.")
        return

    create_vector_store(all_chunks)

    print("\nVector store rebuild completed.")


if __name__ == "__main__":
    main()


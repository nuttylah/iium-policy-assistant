from pathlib import Path

from rag.pdf_processor import process_pdf
from rag.vector_store import create_vector_store


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"


def main():
    all_chunks = []

    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {DOCUMENTS_DIR}"
        )

    print(f"Found {len(pdf_files)} PDF files.\n")

    for pdf_file in pdf_files:
        print("=" * 60)
        print(f"Processing: {pdf_file.name}")
        print("=" * 60)

        chunks = process_pdf(str(pdf_file))

        print(f"Chunks extracted: {len(chunks)}\n")

        all_chunks.extend(chunks)

    print("=" * 60)
    print(f"Total chunks from all PDFs: {len(all_chunks)}")
    print("=" * 60)

    create_vector_store(all_chunks)


if __name__ == "__main__":
    main()
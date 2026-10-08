from pathlib import Path
from rag.pdf_processor import process_pdf


documents_folder = Path("data/documents")

pdf_files = list(documents_folder.glob("*.pdf"))

print(f"\nFound {len(pdf_files)} PDF files.")


for pdf_path in pdf_files:

    print("\n" + "#" * 80)
    print(f"PDF: {pdf_path.name}")
    print("#" * 80)

    chunks = process_pdf(str(pdf_path))

    print(f"Total chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks, start=1):

        metadata = chunk["metadata"]

        print(
            f"Chunk {i} | "
            f"Page {metadata['page']} | "
            f"Kulliyyah: {metadata['kulliyyah']}"
        )
from pathlib import Path
from rag.pdf_processor import process_pdf


documents_folder = Path("data/documents")
output_file = Path("data/all_chunks.txt")

pdf_files = list(documents_folder.glob("*.pdf"))

with open(output_file, "w", encoding="utf-8") as file:

    file.write("IIUM RAG - ALL EXTRACTED CHUNKS\n")
    file.write("=" * 100 + "\n\n")

    total_chunks = 0

    for pdf_path in pdf_files:

        chunks = process_pdf(str(pdf_path))

        file.write("\n" + "#" * 100 + "\n")
        file.write(f"PDF: {pdf_path.name}\n")
        file.write(f"Total chunks: {len(chunks)}\n")
        file.write("#" * 100 + "\n")

        for i, chunk in enumerate(chunks, start=1):

            file.write("\n" + "=" * 80 + "\n")
            file.write(f"CHUNK {i}\n")
            file.write("=" * 80 + "\n")

            file.write(
                f"Source: {chunk['metadata']['source']}\n"
            )

            file.write(
                f"Page: {chunk['metadata']['page']}\n"
            )

            file.write(
                f"Chunk: {chunk['metadata']['chunk']}\n"
            )

            file.write(
                f"Nationality: {chunk['metadata']['nationality']}\n"
            )

            file.write(
                f"Level: {chunk['metadata']['level']}\n"
            )

            file.write("\nText:\n")
            file.write(chunk["text"])
            file.write("\n")

            total_chunks += 1

    file.write("\n\n" + "=" * 100 + "\n")
    file.write(f"TOTAL CHUNKS FROM ALL PDFs: {total_chunks}\n")
    file.write("=" * 100 + "\n")


print("Done!")
print(f"Processed {len(pdf_files)} PDF files.")
print(f"Total chunks: {total_chunks}")
print(f"Saved to: {output_file}")
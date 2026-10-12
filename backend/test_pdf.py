
from pathlib import Path
from collections import Counter
from rag.pdf_processor import process_pdf


documents_folder = Path("data/documents")
pdf_files = sorted(documents_folder.glob("*.pdf"))

print(f"\nFound {len(pdf_files)} PDF files.")

if not pdf_files:
    print("No PDF files found. Check data/documents.")
    raise SystemExit


total_chunks = 0

for pdf_path in pdf_files:
    print("\n" + "#" * 80)
    print(f"PDF: {pdf_path.name}")
    print("#" * 80)

    chunks = process_pdf(str(pdf_path))
    total_chunks += len(chunks)

    chunk_lengths = [len(chunk["text"]) for chunk in chunks]
    programmes = Counter(
        chunk["metadata"].get("programme", "Missing")
        for chunk in chunks
    )
    kulliyyahs = Counter(
        chunk["metadata"].get("kulliyyah", "Missing")
        for chunk in chunks
    )

    print(f"Total chunks: {len(chunks)}")

    if chunk_lengths:
        print(f"Shortest chunk: {min(chunk_lengths)} characters")
        print(f"Longest chunk: {max(chunk_lengths)} characters")
        print(
            f"Average chunk length: "
            f"{sum(chunk_lengths) / len(chunk_lengths):.1f} characters"
        )

    print("\nProgramme metadata:")
    for programme, count in programmes.items():
        print(f"  {programme}: {count}")

    print("\nKulliyyah metadata:")
    for kulliyyah, count in kulliyyahs.items():
        print(f"  {kulliyyah}: {count}")

    missing_fields = Counter()
    for chunk in chunks:
        metadata = chunk["metadata"]

        for field in (
            "source",
            "page",
            "chunk",
            "nationality",
            "level",
            "kulliyyah",
            "programme",
        ):
            if field not in metadata or metadata[field] in (None, ""):
                missing_fields[field] += 1

    print("\nMissing metadata:")
    if missing_fields:
        for field, count in missing_fields.items():
            print(f"  {field}: {count} chunks")
    else:
        print("  None")

    print("\nSample chunks:")
    for i, chunk in enumerate(chunks[:3], start=1):
        metadata = chunk["metadata"]
        preview = " ".join(chunk["text"].split())[:250]

        print(
            f"\nChunk {i} | Page {metadata['page']} | "
            f"Kulliyyah: {metadata['kulliyyah']} | "
            f"Programme: {metadata.get('programme', 'Missing')}"
        )
        print(f"Text: {preview}...")


print("\n" + "=" * 80)
print(f"TOTAL CHUNKS ACROSS ALL PDFs: {total_chunks}")
print("=" * 80)
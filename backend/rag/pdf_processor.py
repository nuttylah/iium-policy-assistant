from pathlib import Path
import re
import pymupdf


MIN_PAGE_CHARS = 100
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while keeping paragraph structure.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_document_metadata(filename: str) -> dict:
    """
    Extract nationality and study level from the PDF filename.
    """

    filename_upper = filename.upper()

    # Detect nationality
    if "INTERNATIONAL" in filename_upper:
        nationality = "International"
    elif "MALAYSIAN" in filename_upper:
        nationality = "Malaysian"
    else:
        nationality = "Malaysian"

    # Detect study level
    if "MASTER" in filename_upper:
        level = "Master"
    elif "UNDERGRADUATED" in filename_upper:
        level = "Undergraduate"
    else:
        level = "Unknown"

    return {
        "nationality": nationality,
        "level": level
    }


def extract_kulliyyah(text: str) -> str:
    """
    Detect the Kulliyyah or academic unit from the PDF text.
    """

    text_upper = text.upper()

    kulliyyah_patterns = {
        "KICT": [
            "KULLIYYAH OF INFORMATION AND COMMUNICATION TECHNOLOGY",
            "(KICT)"
        ],

        "KOP": [
            "KULLIYYAH OF PHARMACY",
            "(KOP)"
        ],

        "KOS": [
            "KULLIYYAH OF SCIENCE",
            "(KOS)"
        ],

        "AIKOL": [
            "AHMAD IBRAHIM KULLIYYAH OF LAWS",
            "(AIKOL)"
        ],

        "KENMS": [
            "KULLIYYAH OF ECONOMICS AND MANAGEMENT SCIENCES",
            "(KENMS)"
        ],

        "KAHS": [
            "KULLIYYAH OF ALLIED HEALTH SCIENCES",
            "(KAHS)"
        ],

        "KOD": [
            "KULLIYYAH OF DENTISTRY",
            "(KOD)"
        ],

        "KOM": [
            "KULLIYYAH OF MEDICINE",
            "(KOM)"
        ],

        "KON": [
            "KULLIYYAH OF NURSING",
            "(KON)"
        ],

        "KOE": [
            "KULLIYYAH OF ENGINEERING",
            "(KOE)"
        ],

        "KAED": [
            "KULLIYYAH OF ARCHITECTURE AND ENVIROMENTAL DESIGN",
            "KULLIYYAH OF ARCHITECTURE AND ENVIRONMENTAL DESIGN",
            "(KAED)"
        ],

        "KOED": [
            "KULLIYYAH OF EDUCATION",
            "(KOED)"
        ],

        "AHAS KIRKHS": [
            "ABDULHAMID ABUSULAYMAN KULLIYYAH OF ISLAMIC REVEALED KNOWLEDGE AND HUMAN SCIENCES",
            "(AHAS KIRKHS)"
        ],

        "KSTCL": [
            "KULLIYYAH OF SUSTAINABLE TOURISM AND CONTEMPORARY LANGUAGES",
            "TMGT"
        ],

        "CELPAD": [
            "PRE-SESSIONAL",
            "CELPAD"
        ]
    }

    for kulliyyah, patterns in kulliyyah_patterns.items():
        for pattern in patterns:
            if pattern in text_upper:
                return kulliyyah

    # Special case for ODL
    if "OPEN AND DISTANCE LEARNING" in text_upper:
        return "ODL"

    return "Unknown"

def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> list[str]:
    """
    Split text into manageable chunks while preserving paragraph boundaries.
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        if len(current_chunk) + len(paragraph) + 1 <= chunk_size:
            current_chunk = (
                f"{current_chunk}\n{paragraph}".strip()
            )

        else:
            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    # Add overlap between chunks
    if chunk_overlap > 0 and len(chunks) > 1:

        overlapped_chunks = [chunks[0]]

        for i in range(1, len(chunks)):

            previous_chunk = chunks[i - 1]
            overlap_text = previous_chunk[-chunk_overlap:]

            new_chunk = f"{overlap_text}\n{chunks[i]}".strip()

            overlapped_chunks.append(new_chunk)

        chunks = overlapped_chunks

    return chunks


def process_pdf(pdf_path: str) -> list[dict]:
    """
    Extract pages from a PDF, clean the text, split it into chunks,
    and preserve source/page/document metadata.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    all_chunks = []

    # Extract document-level metadata from filename
    document_metadata = extract_document_metadata(pdf_path.name)

    # Keep track of the latest detected Kulliyyah
    current_kulliyyah = "Unknown"

    with pymupdf.open(pdf_path) as pdf:

        for page_number, page in enumerate(pdf, start=1):

            raw_text = page.get_text("text")
            text = clean_text(raw_text)

            # Ignore pages with very little useful text
            if len(text) < MIN_PAGE_CHARS:
                continue

            # Try to detect Kulliyyah from the page
            detected_kulliyyah = extract_kulliyyah(text)

            if detected_kulliyyah != "Unknown":
                current_kulliyyah = detected_kulliyyah

            chunks = chunk_text(text)

            for chunk_number, chunk in enumerate(chunks, start=1):

                # Try to detect Kulliyyah directly from the chunk
                chunk_kulliyyah = extract_kulliyyah(chunk)

                if chunk_kulliyyah != "Unknown":
                    kulliyyah = chunk_kulliyyah
                else:
                    kulliyyah = current_kulliyyah

                all_chunks.append(
                    {
                        "text": chunk,
                        "metadata": {
                            "source": pdf_path.name,
                            "page": page_number,
                            "chunk": chunk_number,
                            "nationality": document_metadata["nationality"],
                            "level": document_metadata["level"],
                            "kulliyyah": kulliyyah
                        }
                    }
                )

    return all_chunks

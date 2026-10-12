
from pathlib import Path
import re
import pymupdf


MIN_PAGE_CHARS = 100
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def clean_text(text: str) -> str:
    """Clean extracted PDF text while keeping paragraph structure."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_document_metadata(filename: str) -> dict:
    """Extract nationality and study level from the PDF filename."""
    filename_upper = filename.upper()

    if "INTERNATIONAL" in filename_upper:
        nationality = "International"
    elif "MALAYSIAN" in filename_upper:
        nationality = "Malaysian"
    else:
        nationality = "Unknown"

    if "MASTER" in filename_upper:
        level = "Master"
    elif "UNDERGRADUATED" in filename_upper:
        level = "Undergraduate"
    else:
        level = "Unknown"

    return {
        "nationality": nationality,
        "level": level,
    }


def extract_kulliyyah(text: str) -> str:
    """Detect the Kulliyyah or academic unit from PDF text."""
    text_upper = text.upper()

    kulliyyah_patterns = {
        "KICT": [
            "KULLIYYAH OF INFORMATION AND COMMUNICATION TECHNOLOGY",
            "(KICT)",
        ],
        "KOP": [
            "KULLIYYAH OF PHARMACY",
            "(KOP)",
        ],
        "KOS": [
            "KULLIYYAH OF SCIENCE",
            "(KOS)",
        ],
        "AIKOL": [
            "AHMAD IBRAHIM KULLIYYAH OF LAWS",
            "(AIKOL)",
        ],
        "KENMS": [
            "KULLIYYAH OF ECONOMICS AND MANAGEMENT SCIENCES",
            "(KENMS)",
        ],
        "KAHS": [
            "KULLIYYAH OF ALLIED HEALTH SCIENCES",
            "(KAHS)",
        ],
        "KOD": [
            "KULLIYYAH OF DENTISTRY",
            "(KOD)",
        ],
        "KOM": [
            "KULLIYYAH OF MEDICINE",
            "(KOM)",
        ],
        "KON": [
            "KULLIYYAH OF NURSING",
            "(KON)",
        ],
        "KOE": [
            "KULLIYYAH OF ENGINEERING",
            "(KOE)",
        ],
        "KAED": [
            "KULLIYYAH OF ARCHITECTURE AND ENVIRONMENTAL DESIGN",
            "KULLIYYAH OF ARCHITECTURE AND ENVIROMENTAL DESIGN",
            "(KAED)",
        ],
        "KOED": [
            "KULLIYYAH OF EDUCATION",
            "(KOED)",
        ],
        "AHAS KIRKHS": [
            "ABDULHAMID ABUSULAYMAN KULLIYYAH OF ISLAMIC REVEALED KNOWLEDGE AND HUMAN SCIENCES",
            "(AHAS KIRKHS)",
        ],
        "KSTCL": [
            "KULLIYYAH OF SUSTAINABLE TOURISM AND CONTEMPORARY LANGUAGES",
            "TMGT",
        ],
        "CELPAD": [
            "PRE-SESSIONAL",
            "CELPAD",
        ],
    }

    for kulliyyah, patterns in kulliyyah_patterns.items():
        if any(pattern in text_upper for pattern in patterns):
            return kulliyyah

    if "OPEN AND DISTANCE LEARNING" in text_upper:
        return "ODL"

    return "Unknown"


def extract_programme(text: str) -> str:
    """Detect a programme when its identifying text is present."""
    text_upper = text.upper()

    programme_patterns = {
        "Software Engineering": ["SOFTWARE ENGINEERING"],
        "Information Systems": ["INFORMATION SYSTEMS"],
        "Information Technology": ["INFORMATION TECHNOLOGY"],
        "Computer Science": ["COMPUTER SCIENCE"],
        "Pharmacy": [
            "BACHELOR OF PHARMACY",
            "MASTER OF PHARMACY",
        ],
        "Dentistry": [
            "DOCTOR OF DENTAL SURGERY",
            "BACHELOR OF DENTAL SURGERY",
        ],
        "Medicine": [
            "KULLIYYAH OF MEDICINE",
            "DOCTOR OF MEDICINE",
            "BACHELOR OF MEDICINE",
        ],
        "Engineering": ["KULLIYYAH OF ENGINEERING"],
    }

    for programme, patterns in programme_patterns.items():
        if any(pattern in text_upper for pattern in patterns):
            return programme

    return "Unknown"


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text at paragraph and sentence boundaries where possible.
    Maintain overlap without exceeding the maximum chunk size.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size"
        )

    text = text.strip()

    if not text:
        return []

    # Preserve paragraph boundaries when preparing text segments.
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    segments = []

    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            segments.append(paragraph)
            continue

        # Split long paragraphs at sentence boundaries where possible.
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        buffer = ""

        for sentence in sentences:
            if len(sentence) > chunk_size:
                if buffer:
                    segments.append(buffer)
                    buffer = ""

                # Split exceptionally long sentences into bounded pieces.
                start = 0
                while start < len(sentence):
                    end = min(start + chunk_size, len(sentence))
                    segments.append(sentence[start:end].strip())

                    if end >= len(sentence):
                        break

                    start = end - chunk_overlap

                continue

            candidate = f"{buffer} {sentence}".strip()

            if buffer and len(candidate) > chunk_size:
                segments.append(buffer)
                buffer = sentence
            else:
                buffer = candidate

        if buffer:
            segments.append(buffer)

    # Combine adjacent segments while respecting the maximum size.
    base_chunks = []
    current = ""

    for segment in segments:
        candidate = f"{current}\n\n{segment}".strip()

        if current and len(candidate) > chunk_size:
            base_chunks.append(current)
            current = segment
        else:
            current = candidate

    if current:
        base_chunks.append(current)

    if chunk_overlap == 0 or len(base_chunks) <= 1:
        return base_chunks

    # Add overlap while ensuring every output chunk stays within chunk_size.
    chunks = [base_chunks[0]]

    for current in base_chunks[1:]:
        previous = chunks[-1]
        overlap = previous[-chunk_overlap:].strip()

        # Reserve space for overlap and its separating newline.
        available = chunk_size - len(overlap) - 1

        if available <= 0:
            chunks.append(current[:chunk_size])
            remaining = current[chunk_size:]
        else:
            current_part = current[:available].strip()
            combined = f"{overlap}\n{current_part}".strip()
            chunks.append(combined)
            remaining = current[len(current_part):].strip()

        # Preserve any text that could not fit into the overlapped chunk.
        while remaining:
            next_chunk = remaining[:chunk_size]
            chunks.append(next_chunk)
            remaining = remaining[len(next_chunk):].strip()

    return chunks


def process_pdf(pdf_path: str) -> list[dict]:
    """Extract PDF text, split it into chunks, and preserve metadata."""
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    all_chunks = []
    document_metadata = extract_document_metadata(pdf_path.name)
    current_kulliyyah = "Unknown"

    with pymupdf.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            raw_text = page.get_text("text", sort=True)
            text = clean_text(raw_text)

            if len(text) < MIN_PAGE_CHARS:
                continue

            detected_kulliyyah = extract_kulliyyah(text)

            if detected_kulliyyah != "Unknown":
                current_kulliyyah = detected_kulliyyah

            chunks = chunk_text(text)

            for chunk_number, chunk in enumerate(chunks, start=1):
                chunk_kulliyyah = extract_kulliyyah(chunk)

                if chunk_kulliyyah != "Unknown":
                    kulliyyah = chunk_kulliyyah
                else:
                    kulliyyah = current_kulliyyah

                programme = extract_programme(chunk)

                all_chunks.append({
                    "text": chunk,
                    "metadata": {
                        "source": pdf_path.name,
                        "page": page_number,
                        "chunk": chunk_number,
                        "nationality": document_metadata["nationality"],
                        "level": document_metadata["level"],
                        "kulliyyah": kulliyyah,
                        "programme": programme,
                    },
                })

    return all_chunks

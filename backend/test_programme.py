
from rag.pdf_processor import extract_programme

test_cases = [
    ("Bachelor of Computer Science", "Computer Science"),
    ("Bachelor of Software Engineering", "Software Engineering"),
    ("Bachelor of Information Technology", "Information Technology"),
    ("Bachelor of Pharmacy", "Pharmacy"),
    ("KULLIYYAH OF MEDICINE", "Medicine"),
    ("Some unrelated text", "Unknown"),
]

print("=" * 60)
print("PROGRAMME EXTRACTION TEST")
print("=" * 60)

for text, expected in test_cases:
    actual = extract_programme(text)

    status = "PASS" if actual == expected else "FAIL"

    print(f"{status} | Expected: {expected} | Actual: {actual}")

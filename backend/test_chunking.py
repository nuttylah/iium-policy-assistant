
from rag.pdf_processor import chunk_text, CHUNK_SIZE, CHUNK_OVERLAP


# Test 1: Empty text
assert chunk_text("") == []
print("PASS: Empty text")


# Test 2: Short text
short_text = "This is a short test paragraph."
assert chunk_text(short_text) == [short_text]
print("PASS: Short text")


# Test 3: Long text must stay within the chunk size
long_text = ("This is a sample sentence for testing. " * 200)
chunks = chunk_text(long_text)

assert len(chunks) > 1
assert all(len(chunk) <= CHUNK_SIZE for chunk in chunks)
print(f"PASS: Chunk size limit ({len(chunks)} chunks)")


# Test 4: Every non-whitespace word must remain represented
original_words = long_text.split()
chunk_words = " ".join(chunks).split()

# Check word order and completeness, allowing overlap between chunks.
position = 0
for word in chunk_words:
    if position < len(original_words) and word == original_words[position]:
        position += 1

assert position == len(original_words), (
    f"Some text may be missing. Matched {position} "
    f"of {len(original_words)} original words."
)
print("PASS: Original word sequence preserved")


# Test 5: Confirm consecutive chunks overlap
if len(chunks) > 1:
    previous_end = chunks[0][-CHUNK_OVERLAP:]
    assert any(
        previous_end in chunk
        for chunk in chunks[1:]
    ), "Expected overlap was not detected."

    print("PASS: Chunk overlap detected")

print("\nAll chunking tests passed.")

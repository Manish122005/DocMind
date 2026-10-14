from app.chunker import chunk_text

sample = "DocMind helps researchers find evidence. " * 60

chunks = chunk_text(sample)

print("Total chunks:", len(chunks))
print("First chunk length:", len(chunks[0]))
print("First chunk preview:", chunks[0][:100])

assert len(chunks) > 1
assert all(len(chunk) <= 800 for chunk in chunks)
assert chunk_text("") == []

print("Chunking tests passed!")

# Check that no chunk exceeds the configured size.
for chunk in chunks:
    assert len(chunk) <= 800, "A chunk exceeds 800 characters"

# Check that all generated chunks contain text.
assert all(chunk.strip() for chunk in chunks)

print("Chunk size and empty-chunk checks passed!")
# Check that adjacent chunks share some text.
if len(chunks) > 1:
    shared_text = chunks[0][-50:]
    assert shared_text in chunks[1], "Expected overlap was not found"

print("Chunk overlap check passed!")

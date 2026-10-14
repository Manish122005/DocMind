from app.semantic_search import search_chunks

chunks = [
    "RAG retrieves relevant document passages and supplies them to a language model.",
    "Photosynthesis allows plants to convert light into chemical energy.",
    "Embeddings represent text as numerical vectors for semantic comparison.",
    "A database stores and organizes structured information.",
]

results = search_chunks(
    chunks, "How does retrieval augmented generation find information?", top_k=2
)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Text: {result['text']}\n")

assert results
assert "RAG" in results[0]["text"]
print("Semantic search test passed!")

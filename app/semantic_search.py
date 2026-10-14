import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def search_chunks(chunks, query, top_k=3):
    if not chunks or not query.strip():
        return []

    vectors = model.encode(chunks, normalize_embeddings=True)
    vectors = np.asarray(vectors, dtype="float32")

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    query_vector = model.encode(
        [query],
        normalize_embeddings=True
    )
    query_vector = np.asarray(query_vector, dtype="float32")

    k = min(top_k, len(chunks))
    scores, indices = index.search(query_vector, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0:
            results.append({
                "index": int(idx),
                "text": chunks[idx],
                "score": float(score)
            })

    return results
def retrieve(query_embedding, store, k=3):
    scored = [(cosine(query_embedding, d["embedding"]), d) for d in store]
    return [d for score, d in scored if score >= SIMILARITY_THRESHOLD][:k]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb)
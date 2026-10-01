import numpy as np

def cosine_similarity(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.ndim != 1 or b.ndim != 1 or a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('Vectors must be finite one-dimensional arrays of equal length')
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denominator) if denominator else 0.0

class VectorIndex:
    def __init__(self, embeddings):
        self.embeddings = embeddings
    def retrieve(self, embedding):
        # Unordered candidates: sorting belongs to RankingService.
        return [(pid, cosine_similarity(embedding, vector)) for pid, vector in self.embeddings.items()]

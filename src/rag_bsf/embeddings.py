from __future__ import annotations

import hashlib
import math
import re

from rag_bsf.config import DEFAULT_EMBEDDING_DIMENSIONS


TOKEN_RE = re.compile(r"[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ]{2,}")


class HashingEmbedder:
    """Deterministic local embedding model for the Ticket 3 prototype."""

    model_name = "local-hashing-v1"

    def __init__(self, dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS):
        if dimensions <= 0:
            raise ValueError("Embedding dimensions must be greater than zero.")
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = TOKEN_RE.findall(text.lower())
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        return normalize(vector)

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


def normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(left_value * right_value for left_value, right_value in zip(left, right))
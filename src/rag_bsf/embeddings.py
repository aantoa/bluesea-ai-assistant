from __future__ import annotations

import hashlib
import math
import os
import re
from pathlib import Path

from rag_bsf.config import DEFAULT_EMBEDDING_DIMENSIONS, DEFAULT_EMBEDDING_MODEL


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


class SentenceTransformerEmbedder:
    """Multilingual semantic embedder for cross-language RAG retrieval."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self.model_name = model_name.strip() or DEFAULT_EMBEDDING_MODEL
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is required for multilingual embeddings. "
                "Install dependencies with: pip install -r requirements.txt"
            ) from exc

        self._model = SentenceTransformer(self.model_name)
        self.dimensions = int(self._model.get_sentence_embedding_dimension())

    def embed(self, text: str) -> list[float]:
        if not text.strip():
            return [0.0] * self.dimensions
        vector = self._model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vector.astype(float).tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.astype(float).tolist()


def get_embedder():
    """Build the configured embedding model.

    Use EMBEDDING_MODEL=local-hashing-v1 only for offline tests. The default is a
    multilingual sentence-transformers model so Spanish queries can retrieve
    English documents semantically.
    """

    load_env_file()
    model_name = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL).strip()
    if model_name == HashingEmbedder.model_name:
        return HashingEmbedder()
    return SentenceTransformerEmbedder(model_name or DEFAULT_EMBEDDING_MODEL)


def load_env_file() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    for parent in [Path.cwd(), *Path.cwd().parents]:
        env_path = parent / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=False)
            return


def normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(left_value * right_value for left_value, right_value in zip(left, right))
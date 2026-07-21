from __future__ import annotations

import json
from pathlib import Path

from rag_bsf.config import VECTOR_INDEX_FILE
from rag_bsf.embeddings import cosine_similarity
from rag_bsf.schemas import Chunk, IndexedVector, SearchResult


class LocalVectorStore:
    """JSONL vector store used to validate Ticket 3 locally and in Colab."""

    def __init__(self, index_path: Path = VECTOR_INDEX_FILE):
        self.index_path = index_path
        self._items: list[IndexedVector] = []

    def add(
        self,
        chunk: Chunk,
        vector: list[float],
        embedding_model: str,
        dimensions: int,
    ) -> None:
        self._items.append(
            IndexedVector(
                chunk=chunk,
                vector=vector,
                embedding_model=embedding_model,
                dimensions=dimensions,
            )
        )

    def save(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with self.index_path.open("w", encoding="utf-8") as fh:
            for item in self._items:
                fh.write(json.dumps(item.to_dict(), ensure_ascii=False))
                fh.write("\n")

    def load(self) -> None:
        self._items = []
        if not self.index_path.exists():
            return

        with self.index_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                payload = json.loads(line)
                chunk_data = payload["chunk"]
                self._items.append(
                    IndexedVector(
                        chunk=Chunk(
                            chunk_id=chunk_data["chunk_id"],
                            document_id=chunk_data["document_id"],
                            text=chunk_data["text"],
                            metadata=chunk_data["metadata"],
                        ),
                        vector=payload["vector"],
                        embedding_model=payload["embedding_model"],
                        dimensions=payload["dimensions"],
                    )
                )

    def search(self, query_vector: list[float], top_k: int = 5) -> list[SearchResult]:
        ranked: list[SearchResult] = []
        for idx, item in enumerate(self._items, start=1):
            score = cosine_similarity(query_vector, item.vector)
            ranked.append(SearchResult(chunk=item.chunk, score=score, source_label=f"S{idx}"))

        ranked.sort(key=lambda result: result.score, reverse=True)
        results = ranked[:top_k]
        for idx, result in enumerate(results, start=1):
            result.source_label = f"S{idx}"
        return results

    def all_results(self) -> list[SearchResult]:
        """Return every indexed chunk as a SearchResult for lexical/hybrid retrieval."""

        return [
            SearchResult(chunk=item.chunk, score=0.0, source_label=f"S{idx}")
            for idx, item in enumerate(self._items, start=1)
        ]
    
    def __len__(self) -> int:
        return len(self._items)
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DocumentRecord:
    document_id: str
    path: str
    filename: str
    title: str
    document_code: str
    category: str
    owner: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class IndexedVector:
    chunk: Chunk
    vector: list[float]
    embedding_model: str
    dimensions: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk": self.chunk.to_dict(),
            "vector": self.vector,
            "embedding_model": self.embedding_model,
            "dimensions": self.dimensions,
        }
    
@dataclass
class SearchResult:
    chunk: Chunk
    score: float
    source_label: str
    semantic_score: float | None = None
    rerank_score: float | None = None

@dataclass
class RetrievalContext:
    question: str
    context: str
    results: list[SearchResult]
    applied_filters: dict[str, str] = field(default_factory=dict)
    candidate_count: int = 0
    filtered_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "context": self.context,
            "applied_filters": self.applied_filters,
            "candidate_count": self.candidate_count,
            "filtered_count": self.filtered_count,
            "results": [
                {
                    "source_label": result.source_label,
                    "score": result.score,
                    "semantic_score": result.semantic_score,
                    "rerank_score": result.rerank_score,
                    "chunk": result.chunk.to_dict(),
                }
                for result in self.results
            ],
        }
    
@dataclass
class AnswerSource:
    source_label: str
    document_code: str
    title: str
    filename: str
    section: str
    category: str
    owner: str
    score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnswerResult:
    question: str
    answer: str
    sources: list[AnswerSource]
    prompt: str
    grounded: bool
    fallback_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "sources": [source.to_dict() for source in self.sources],
            "prompt": self.prompt,
            "grounded": self.grounded,
            "fallback_reason": self.fallback_reason,
        }

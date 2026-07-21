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

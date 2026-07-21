from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

from rag_bsf.config import (
    CATEGORY_DIR_BY_NAME,
    CHUNKS_FILE,
    DOCUMENT_STATUS_FILE,
    DOCUMENTS_DIR,
    EMBEDDINGS_MANIFEST_FILE,
    INVENTORY_FILE,
    VECTOR_INDEX_FILE,
    PROCESSED_DIR,
)
from rag_bsf.document_loader import discover_markdown_documents, load_inventory_rows
from rag_bsf.embeddings import HashingEmbedder
from rag_bsf.schemas import Chunk, SearchResult
from rag_bsf.text_processing import chunk_document
from rag_bsf.vector_store import LocalVectorStore


def build_inventory(root_dir: Path = DOCUMENTS_DIR) -> list[dict]:
    records = discover_markdown_documents(root_dir=root_dir)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    discovered_by_id = {record.document_id: record for record in records}
    discovered_by_stem = {Path(record.filename).stem: record for record in records}
    inventory: list[dict] = []

    for source_row in load_inventory_rows():
        record = discovered_by_id.get(source_row.get("document_id", ""))
        if not record:
            record = discovered_by_stem.get(Path(source_row.get("file_name", "")).stem)
        inventory.append(
            {
                **source_row,
                "markdown_available": bool(record),
                "local_markdown_path": record.path if record else "",
            }
        )

    known_ids = {item.get("document_id", "") for item in inventory}
    for record in records:
        if record.document_id in known_ids:
            continue
        inventory.append(
            {
                **record.to_dict(),
                "markdown_available": True,
                "local_markdown_path": record.path,
                "inventory_status": "not_listed_in_source_inventory",
            }
        )

    INVENTORY_FILE.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    return inventory


def process_documents(root_dir: Path = DOCUMENTS_DIR) -> dict[str, int]:
    records = discover_markdown_documents(root_dir=root_dir)
    all_chunks: list[Chunk] = []

    for record in records:
        all_chunks.extend(chunk_document(record, root_dir=root_dir))

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with CHUNKS_FILE.open("w", encoding="utf-8") as fh:
        for chunk in all_chunks:
            fh.write(json.dumps(chunk.to_dict(), ensure_ascii=False))
            fh.write("\n")

    build_inventory(root_dir=root_dir)
    return {"documents": len(records), "chunks": len(all_chunks)}

def load_chunks(chunks_file: Path = CHUNKS_FILE) -> list[Chunk]:
    if not chunks_file.exists():
        return []

    chunks: list[Chunk] = []
    with chunks_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            payload = json.loads(line)
            chunks.append(
                Chunk(
                    chunk_id=payload["chunk_id"],
                    document_id=payload["document_id"],
                    text=payload["text"],
                    metadata=payload["metadata"],
                )
            )
    return chunks


def index_chunks(
    chunks_file: Path = CHUNKS_FILE,
    index_file: Path = VECTOR_INDEX_FILE,
    manifest_file: Path = EMBEDDINGS_MANIFEST_FILE,
) -> dict[str, int | str]:
    chunks = load_chunks(chunks_file)
    embedder = HashingEmbedder()
    store = LocalVectorStore(index_file)

    for chunk in chunks:
        store.add(
            chunk=chunk,
            vector=embedder.embed(chunk.text),
            embedding_model=embedder.model_name,
            dimensions=embedder.dimensions,
        )
    store.save()

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_chunks_file": str(chunks_file),
        "source_chunks_sha256": _file_sha256(chunks_file) if chunks_file.exists() else "",
        "vector_index_file": str(index_file),
        "embedding_model": embedder.model_name,
        "dimensions": embedder.dimensions,
        "chunks": len(chunks),
        "vectors": len(store),
    }
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "chunks": len(chunks),
        "vectors": len(store),
        "dimensions": embedder.dimensions,
        "embedding_model": embedder.model_name,
    }


def search_index(question: str, top_k: int = 5, index_file: Path = VECTOR_INDEX_FILE) -> list[SearchResult]:
    embedder = HashingEmbedder()
    store = LocalVectorStore(index_file)
    store.load()
    if len(store) == 0:
        return []
    return store.search(embedder.embed(question), top_k=top_k)

def validate_document_collection(root_dir: Path = DOCUMENTS_DIR) -> dict[str, int]:
    rows = load_inventory_rows()
    status_rows: list[dict[str, str]] = []

    for row in rows:
        expected_path = _expected_source_path(row, root_dir)
        folder = _display_folder(expected_path, root_dir)
        file_name = row.get("file_name", "")
        expected_path = expected_dir / file_name
        markdown_path = expected_path.with_suffix(".md")
        final_available = expected_path.exists()
        markdown_available = markdown_path.exists()

        if final_available and markdown_available:
            status = "final_and_markdown_available"
        elif final_available:
            status = "final_available"
        elif markdown_available:
            status = "markdown_available"
        else:
            status = "missing"

        status_rows.append(
            {
                "document_id": row.get("document_id", ""),
                "title": row.get("title", ""),
                "format": row.get("format", ""),
                "category": row.get("category", ""),
                "expected_folder": folder,
                "expected_file": file_name,
                "final_available": str(final_available).lower(),
                "markdown_available": str(markdown_available).lower(),
                "status": status,
            }
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "document_id",
        "title",
        "format",
        "category",
        "expected_folder",
        "expected_file",
        "final_available",
        "markdown_available",
        "status",
    ]
    with DOCUMENT_STATUS_FILE.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(status_rows)

    return {
        "expected": len(status_rows),
        "final_available": sum(row["final_available"] == "true" for row in status_rows),
        "markdown_available": sum(row["markdown_available"] == "true" for row in status_rows),
        "missing": sum(row["status"] == "missing" for row in status_rows),
    }

def _expected_source_path(row: dict[str, str], root_dir: Path) -> Path:
    relative_path = row.get("relative_path", "")
    if relative_path:
        path = Path(relative_path)
        parts = path.parts
        if parts and parts[0] == root_dir.name:
            path = Path(*parts[1:])
        return root_dir / path

    folder = _folder_for_category(row.get("category", ""))
    file_name = row.get("file_name", "")
    return root_dir / folder / file_name if folder else root_dir / file_name


def _folder_for_category(category: str) -> str:
    if not category:
        return ""

    exact_match = CATEGORY_DIR_BY_NAME.get(category)
    if exact_match:
        return exact_match

    normalized_category = _normalize_lookup_value(category)
    for known_category, folder in CATEGORY_DIR_BY_NAME.items():
        if _normalize_lookup_value(known_category) == normalized_category:
            return folder
    return ""


def _normalize_lookup_value(value: str) -> str:
    return " ".join(value.strip().lower().replace("&", "and").split())


def _display_folder(expected_path: Path, root_dir: Path) -> str:
    try:
        return expected_path.relative_to(root_dir).parts[0]
    except (IndexError, ValueError):
        return ""


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
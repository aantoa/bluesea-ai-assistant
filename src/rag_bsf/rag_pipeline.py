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
    LEGACY_INVENTORY_FILE,
    VECTOR_INDEX_FILE,
    PROCESSED_DIR,
    SOURCE_INVENTORY_FILE,
    SOURCE_EXTENSION_BY_FORMAT,
    SUPPORTED_SOURCE_EXTENSIONS,
)
from rag_bsf.answer_generation import generate_grounded_answer
from rag_bsf.document_loader import build_document_record, discover_source_documents, load_inventory_rows
from rag_bsf.embeddings import HashingEmbedder
from rag_bsf.retrieval import retrieve_context
from rag_bsf.schemas import AnswerResult, Chunk, RetrievalContext, SearchResult
from rag_bsf.text_processing import chunk_document
from rag_bsf.vector_store import LocalVectorStore


def build_inventory(root_dir: Path = DOCUMENTS_DIR) -> list[dict]:
    records = discover_source_documents(root_dir=root_dir)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    discovered_by_id = {record.document_id: record for record in records}
    discovered_by_stem = {Path(record.filename).stem: record for record in records}
    inventory: list[dict] = []

    for source_row in load_inventory_rows(_inventory_file_for_root(root_dir)):
        record = discovered_by_id.get(source_row.get("document_id", ""))
        if not record:
            record = discovered_by_stem.get(Path(source_row.get("file_name", "")).stem)
        record_is_markdown = bool(record and Path(record.filename).suffix.lower() in {".md", ".markdown"})
        inventory.append(
            {
                **source_row,
                "source_available": bool(record),
                "local_source_path": record.path if record else "",
                "markdown_available": record_is_markdown,
                "local_markdown_path": record.path if record_is_markdown and record else "",
            }
        )

    known_ids = {item.get("document_id", "") for item in inventory}
    for record in records:
        if record.document_id in known_ids:
            continue
        record_is_markdown = Path(record.filename).suffix.lower() in {".md", ".markdown"}
        inventory.append(
            {
                **record.to_dict(),
                "source_available": True,
                "local_source_path": record.path,
                "markdown_available": record_is_markdown,
                "local_markdown_path": record.path if record_is_markdown else "",
                "inventory_status": "not_listed_in_source_inventory",
            }
        )

    INVENTORY_FILE.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    return inventory


def process_documents(root_dir: Path = DOCUMENTS_DIR) -> dict[str, int]:
    records = _records_for_processing(root_dir)
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


def _records_for_processing(root_dir: Path) -> list:
    rows = load_inventory_rows(_inventory_file_for_root(root_dir))
    if not rows:
        return discover_source_documents(root_dir=root_dir)

    records = []
    seen_paths: set[Path] = set()
    for row in rows:
        matched_path = _first_existing_path(_candidate_source_paths(row, root_dir))
        if not matched_path or matched_path in seen_paths:
            continue
        records.append(build_document_record(matched_path, root_dir=root_dir))
        seen_paths.add(matched_path)
    return records

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


def retrieve_rag_context(
    question: str,
    top_k: int = 5,
    candidate_k: int = 20,
    metadata_filters: dict[str, str] | None = None,
    index_file: Path = VECTOR_INDEX_FILE,
) -> RetrievalContext:
    return retrieve_context(
        question,
        top_k=top_k,
        candidate_k=candidate_k,
        metadata_filters=metadata_filters,
        index_file=index_file,
    )

def answer_question(
    question: str,
    top_k: int = 5,
    candidate_k: int = 20,
    metadata_filters: dict[str, str] | None = None,
    min_confidence: float = 0.18,
    index_file: Path = VECTOR_INDEX_FILE,
) -> AnswerResult:
    retrieved = retrieve_rag_context(
        question,
        top_k=top_k,
        candidate_k=candidate_k,
        metadata_filters=metadata_filters,
        index_file=index_file,
    )
    return generate_grounded_answer(
        question,
        retrieved,
        min_confidence=min_confidence,
    )

def validate_document_collection(root_dir: Path = DOCUMENTS_DIR) -> dict[str, int]:
    rows = load_inventory_rows(_inventory_file_for_root(root_dir))
    status_rows: list[dict[str, str]] = []

    for row in rows:
        expected_path = _expected_source_path(row, root_dir)
        candidate_paths = _candidate_source_paths(row, root_dir)
        matched_source_path = _first_existing_path(candidate_paths)
        markdown_path = _first_existing_path(
            path for path in candidate_paths if path.suffix.lower() in {".md", ".markdown"}
        )
        folder = _display_folder(expected_path, root_dir)
        file_name = expected_path.name
        source_available = matched_source_path is not None
        final_available = expected_path.exists() or bool(
            matched_source_path and matched_source_path.suffix.lower() == expected_path.suffix.lower()
        )
        markdown_available = markdown_path is not None

        if final_available and markdown_available:
            status = "final_and_markdown_available"
        elif final_available:
            status = "final_available"
        elif source_available:
            status = "source_available_wrong_declared_format"
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
                    "matched_file": matched_source_path.name if matched_source_path else "",
                    "source_available": str(source_available).lower(),
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
        "matched_file",
        "source_available",
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
        "source_available": sum(row["source_available"] == "true" for row in status_rows),
        "final_available": sum(row["final_available"] == "true" for row in status_rows),
        "markdown_available": sum(row["markdown_available"] == "true" for row in status_rows),
        "missing": sum(row["status"] == "missing" for row in status_rows),
    }

def _expected_source_path(row: dict[str, str], root_dir: Path) -> Path:
    raw_path = _raw_inventory_path(row, root_dir)
    declared_extension = _extension_for_format(row.get("format", ""))
    if declared_extension:
        return raw_path.with_suffix(declared_extension)
    return raw_path


def _inventory_file_for_root(root_dir: Path) -> Path:
    configured_inventory = Path(SOURCE_INVENTORY_FILE)
    if configured_inventory.exists() and _is_relative_to(configured_inventory, root_dir):
        return configured_inventory

    inventory_dir = root_dir / "inventory"
    primary = inventory_dir / "BSF-INV-001_Document_Inventory.csv"
    if primary.exists():
        return primary

    configured_legacy_inventory = Path(LEGACY_INVENTORY_FILE)
    if configured_legacy_inventory.exists() and _is_relative_to(configured_legacy_inventory, root_dir):
        return configured_legacy_inventory

    return inventory_dir / "document_inventory.csv"


def _raw_inventory_path(row: dict[str, str], root_dir: Path) -> Path:
    relative_path = row.get("relative_path", "")
    if relative_path:
        path = Path(relative_path)
        parts = path.parts
        if parts and parts[0] == root_dir.name:
            path = Path(*parts[1:])
        if len(path.parts) == 1:
            folder = _folder_for_category(row.get("category", ""))
            return root_dir / folder / path if folder else root_dir / path
        return root_dir / path

    folder = _folder_for_category(row.get("category", ""))
    file_name = row.get("file_name", "") or _fallback_file_name(row)
    return root_dir / folder / file_name if folder else root_dir / file_name


def _fallback_file_name(row: dict[str, str]) -> str:
    stem_parts = [row.get("document_id", "").strip()]
    title = row.get("title", "").strip()
    if title:
        stem_parts.append("_".join(title.replace("/", " ").split()))
    stem = "_".join(part for part in stem_parts if part) or "untitled_document"
    return stem + (_extension_for_format(row.get("format", "")) or ".md")


def _candidate_source_paths(row: dict[str, str], root_dir: Path) -> list[Path]:
    raw_path = _raw_inventory_path(row, root_dir)
    expected_path = _expected_source_path(row, root_dir)
    candidates = [expected_path, raw_path]
    for extension in SUPPORTED_SOURCE_EXTENSIONS:
        candidates.append(expected_path.with_suffix(extension))
        candidates.append(raw_path.with_suffix(extension))
    candidates.extend(_find_existing_sources_by_document_id(row, root_dir))
    return _unique_paths(candidates)


def _extension_for_format(format_name: str) -> str:
    return SOURCE_EXTENSION_BY_FORMAT.get(format_name.strip().upper(), "")


def _first_existing_path(paths) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _find_existing_sources_by_document_id(row: dict[str, str], root_dir: Path) -> list[Path]:
    document_id = (row.get("document_id") or row.get("document_code") or "").strip().lower()
    if not document_id or not root_dir.exists():
        return []

    supported_extensions = set(SUPPORTED_SOURCE_EXTENSIONS)
    matches: list[Path] = []
    for path in sorted(root_dir.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path == _inventory_file_for_root(root_dir):
            continue
        if path.suffix.lower() not in supported_extensions:
            continue
        if path.stem.lower().startswith(document_id):
            matches.append(path)
    return matches


def _unique_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


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

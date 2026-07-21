from __future__ import annotations

import csv
import json
from pathlib import Path

from rag_bsf.config import (
    CATEGORY_DIR_BY_NAME,
    CHUNKS_FILE,
    DOCUMENT_STATUS_FILE,
    DOCUMENTS_DIR,
    INVENTORY_FILE,
    PROCESSED_DIR,
)
from rag_bsf.document_loader import discover_markdown_documents, load_inventory_rows
from rag_bsf.schemas import Chunk
from rag_bsf.text_processing import chunk_document


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


def validate_document_collection(root_dir: Path = DOCUMENTS_DIR) -> dict[str, int]:
    rows = load_inventory_rows()
    status_rows: list[dict[str, str]] = []

    for row in rows:
        folder = CATEGORY_DIR_BY_NAME.get(row.get("category", ""), "")
        expected_dir = root_dir / folder if folder else root_dir
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
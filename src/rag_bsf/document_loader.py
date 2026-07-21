from __future__ import annotations

import csv
import re
from pathlib import Path

from rag_bsf.config import (
    CATEGORY_DIR_BY_NAME,
    DOCUMENTS_DIR,
    LEGACY_INVENTORY_FILE,
    MARKDOWN_SOURCE_DIRS,
    SOURCE_INVENTORY_FILE,
)
from rag_bsf.schemas import DocumentRecord


DOCUMENT_CODE_RE = re.compile(r"(BSF-[A-Z]+(?:-[A-Z]+)*-\d+)")
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*\n", re.DOTALL)


def load_inventory_rows(inventory_path: Path = SOURCE_INVENTORY_FILE) -> list[dict[str, str]]:
    if not inventory_path.exists() and inventory_path == SOURCE_INVENTORY_FILE:
        inventory_path = LEGACY_INVENTORY_FILE

    if not inventory_path.exists():
        return []

    rows: list[dict[str, str]] = []
    with inventory_path.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            rows.append(normalize_inventory_row(row))
    return rows


def normalize_inventory_row(row: dict[str, str]) -> dict[str, str]:
    cleaned = {key: (value or "").strip() for key, value in row.items() if key}

    document_id = cleaned.get("document_id") or cleaned.get("document_code", "")
    file_name = cleaned.get("file_name") or cleaned.get("current_file_name", "")
    title = cleaned.get("title") or cleaned.get("document_title", "")
    category = (
        cleaned.get("category")
        or cleaned.get("business_area")
        or cleaned.get("document_category", "")
    )
    owner = cleaned.get("owner") or cleaned.get("document_owner", "")
    status = cleaned.get("status") or cleaned.get("document_status", "")
    review_date = cleaned.get("review_date") or cleaned.get("next_review_date", "")

    return {
        **cleaned,
        "document_id": document_id,
        "document_code": cleaned.get("document_code") or document_id,
        "file_name": file_name,
        "title": title,
        "category": category,
        "owner": owner,
        "status": status,
        "review_date": review_date,
    }


def load_inventory_metadata(inventory_path: Path = SOURCE_INVENTORY_FILE) -> dict[str, dict[str, str]]:
    metadata_by_key: dict[str, dict[str, str]] = {}
    for row in load_inventory_rows(inventory_path):
        for key in _inventory_lookup_keys(row):
            metadata_by_key[key] = row
    return metadata_by_key


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_front_matter(markdown: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER_RE.match(markdown)
    if not match:
        return {}, markdown

    metadata: dict[str, str] = {}
    for raw_line in match.group("body").splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')

    return metadata, markdown[match.end() :]


def infer_document_code(path: Path, metadata: dict[str, str]) -> str:
    for value in (metadata.get("code"), metadata.get("document_code"), path.stem):
        if not value:
            continue
        match = DOCUMENT_CODE_RE.search(value)
        if match:
            return match.group(1)
    return "UNCLASSIFIED"


def infer_title(markdown_body: str, path: Path, metadata: dict[str, str]) -> str:
    if metadata.get("title"):
        return metadata["title"]
    for line in markdown_body.splitlines():
        if line.startswith("# "):
            return line.lstrip("#").strip()
    return path.stem.replace("_", " ").replace("-", " ").strip()


def _inventory_lookup_keys(row: dict[str, str]) -> set[str]:
    keys = {
        row.get("document_id", ""),
        row.get("file_name", ""),
        Path(row.get("file_name", "")).stem,
    }
    return {key.lower() for key in keys if key}


def find_inventory_row(
    path: Path,
    document_code: str,
    inventory: dict[str, dict[str, str]],
) -> dict[str, str]:
    candidates = [
        document_code,
        path.name,
        path.stem,
    ]
    for candidate in candidates:
        row = inventory.get(candidate.lower())
        if row:
            return row
    return {}


def infer_category_from_path(path: Path, root_dir: Path = DOCUMENTS_DIR) -> str:
    try:
        top_level_folder = path.relative_to(root_dir).parts[0]
    except (IndexError, ValueError):
        return "Uncategorized"
    return CATEGORY_DIR_BY_NAME.get(top_level_folder, "Uncategorized")


def build_document_record(path: Path, root_dir: Path = DOCUMENTS_DIR) -> DocumentRecord:
    inventory = load_inventory_metadata()
    markdown = read_markdown(path)
    metadata, body = extract_front_matter(markdown)
    document_code = infer_document_code(path, metadata)
    inventory_row = find_inventory_row(path, document_code, inventory)
    relative_path = str(path.relative_to(root_dir))
    title = metadata.get("title") or inventory_row.get("title") or infer_title(body, path, metadata)
    document_id = inventory_row.get("document_id") or document_code
    if document_id == "UNCLASSIFIED":
        document_id = relative_path

    return DocumentRecord(
        document_id=document_id,
        path=relative_path,
        filename=path.name,
        title=title,
        document_code=inventory_row.get("document_id") or document_code,
        category=metadata.get("category") or inventory_row.get("category") or infer_category_from_path(path, root_dir),
        owner=metadata.get("owner") or inventory_row.get("owner") or "Unassigned",
        metadata={**inventory_row, **metadata},
    )


def discover_markdown_documents(root_dir: Path = DOCUMENTS_DIR) -> list[DocumentRecord]:
    source_dirs = MARKDOWN_SOURCE_DIRS if root_dir == DOCUMENTS_DIR else (root_dir,)

    records: list[DocumentRecord] = []
    for source_dir in source_dirs:
        if not source_dir.exists():
            continue
        for path in sorted(source_dir.rglob("*.md")):
            if path.name.startswith("."):
                continue
            records.append(build_document_record(path, root_dir=root_dir))
    return records
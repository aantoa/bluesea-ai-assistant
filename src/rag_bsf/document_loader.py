from __future__ import annotations

import csv
import json
import re
import zipfile
from html import unescape
from pathlib import Path
from xml.etree import ElementTree

from rag_bsf.config import (
    CATEGORY_DIR_BY_NAME,
    DOCUMENTS_DIR,
    LEGACY_INVENTORY_FILE,
    SOURCE_INVENTORY_FILE,
    SUPPORTED_SOURCE_EXTENSIONS,
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
    relative_path = (
            cleaned.get("relative_path")
            or cleaned.get("current_relative_path")
            or cleaned.get("local_source_path", "")
    )

    return {
        **cleaned,
        "document_id": document_id,
        "document_code": cleaned.get("document_code") or document_id,
        "file_name": file_name,
        "relative_path": relative_path,
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


def read_document_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown", ".txt"}:
        return path.read_text(encoding="utf-8")
    if suffix in {".html", ".htm"}:
        return _extract_html_text(path)
    if suffix == ".json":
        return _extract_json_text(path)
    if suffix in {".csv", ".tsv"}:
        return _extract_delimited_text(path)
    if suffix == ".docx":
        return _extract_docx_text(path)
    if suffix == ".pptx":
        return _extract_pptx_text(path)
    if suffix == ".xlsx":
        return _extract_xlsx_text(path)
    if suffix == ".pdf":
        return _extract_pdf_text(path)
    return ""


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
    raw_text = read_document_text(path)
    metadata, body = extract_front_matter(raw_text) if path.suffix.lower() in {".md", ".markdown"} else ({}, raw_text)
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
        metadata={
            **inventory_row,
            **metadata,
            "source_format": path.suffix.lower().lstrip("."),
        },
    )


def discover_markdown_documents(root_dir: Path = DOCUMENTS_DIR) -> list[DocumentRecord]:
    return discover_source_documents(root_dir=root_dir)


def discover_source_documents(root_dir: Path = DOCUMENTS_DIR) -> list[DocumentRecord]:
    records: list[DocumentRecord] = []
    supported_extensions = set(SUPPORTED_SOURCE_EXTENSIONS)
    if not root_dir.exists():
        return records

    for path in sorted(root_dir.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in supported_extensions:
            continue
        records.append(build_document_record(path, root_dir=root_dir))
    return records


def _extract_html_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return unescape(text)


def _extract_json_text(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return "\n".join(_flatten_json(payload))


def _flatten_json(value: object, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            lines.extend(_flatten_json(child, child_prefix))
        return lines
    if isinstance(value, list):
        lines = []
        for idx, child in enumerate(value, start=1):
            child_prefix = f"{prefix}[{idx}]" if prefix else f"item[{idx}]"
            lines.extend(_flatten_json(child, child_prefix))
        return lines
    return [f"{prefix}: {value}" if prefix else str(value)]


def _extract_delimited_text(path: Path) -> str:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    lines: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh, delimiter=delimiter)
        headers = next(reader, [])
        if headers:
            lines.append(" | ".join(cell.strip() for cell in headers if cell.strip()))
        for row_number, row in enumerate(reader, start=2):
            pairs = [
                f"{header.strip()}: {value.strip()}"
                for header, value in zip(headers, row)
                if header.strip() and value.strip()
            ]
            if pairs:
                lines.append(f"Row {row_number}: " + " | ".join(pairs))
            else:
                lines.append(" | ".join(cell.strip() for cell in row if cell.strip()))
    return "\n".join(line for line in lines if line)


def _extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml_bytes = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml_bytes)
    lines: list[str] = []
    for paragraph in root.iter():
        if _local_name(paragraph.tag) != "p":
            continue
        paragraph_text = " ".join(_iter_xml_text(paragraph, "t")).strip()
        if paragraph_text:
            lines.append(paragraph_text)
    return "\n\n".join(lines)


def _extract_pptx_text(path: Path) -> str:
    texts: list[str] = []
    with zipfile.ZipFile(path) as archive:
        slide_names = sorted(name for name in archive.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
        for slide_number, slide_name in enumerate(slide_names, start=1):
            root = ElementTree.fromstring(archive.read(slide_name))
            slide_text = "\n".join(_iter_xml_text(root, "t"))
            if slide_text:
                texts.append(f"# Slide {slide_number}\n{slide_text}")

        note_names = sorted(name for name in archive.namelist() if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml"))
        for note_number, note_name in enumerate(note_names, start=1):
            root = ElementTree.fromstring(archive.read(note_name))
            note_text = "\n".join(_iter_xml_text(root, "t"))
            if note_text:
                texts.append(f"# Slide {note_number} Notes\n{note_text}")
    return "\n\n".join(texts)


def _extract_xlsx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        shared_strings = _load_xlsx_shared_strings(archive)
        worksheet_names = sorted(name for name in archive.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"))
        lines: list[str] = []
        sheet_names = _load_xlsx_sheet_names(archive)
        for sheet_index, worksheet_name in enumerate(worksheet_names, start=1):
            sheet_label = sheet_names.get(sheet_index, f"Sheet {sheet_index}")
            lines.append(f"# {sheet_label}")
            root = ElementTree.fromstring(archive.read(worksheet_name))
            headers: list[str] = []
            for row in root.iter():
                if _local_name(row.tag) != "row":
                    continue
                values = [_xlsx_cell_value(cell, shared_strings) for cell in row if _local_name(cell.tag) == "c"]
                if not values:
                    continue
                if not headers:
                    headers = values
                    line = " | ".join(value for value in headers if value)
                else:
                    pairs = [
                        f"{header}: {value}"
                        for header, value in zip(headers, values)
                        if header and value
                    ]
                    row_number = row.attrib.get("r", "")
                    line = f"Row {row_number}: " + " | ".join(pairs) if pairs else " | ".join(value for value in values if value)
                if line:
                    lines.append(line)
    return "\n".join(lines)


def _extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""

    reader = PdfReader(str(path))
    pages: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(f"# Page {page_number}\n{page_text.strip()}")
    return "\n\n".join(pages)


def _load_xlsx_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(_iter_xml_text(item, "t")) for item in root if _local_name(item.tag) == "si"]


def _load_xlsx_sheet_names(archive: zipfile.ZipFile) -> dict[int, str]:
    try:
        root = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    except KeyError:
        return {}
    names: dict[int, str] = {}
    for idx, sheet in enumerate((node for node in root.iter() if _local_name(node.tag) == "sheet"), start=1):
        names[idx] = sheet.attrib.get("name", f"Sheet {idx}")
    return names


def _xlsx_cell_value(cell: ElementTree.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t", "")
    if cell_type == "inlineStr":
        return " ".join(_iter_xml_text(cell, "t")).strip()

    raw_value = ""
    for child in cell:
        if _local_name(child.tag) == "v" and child.text:
            raw_value = child.text.strip()
            break
    if cell_type == "s" and raw_value.isdigit():
        idx = int(raw_value)
        return shared_strings[idx] if idx < len(shared_strings) else ""
    return raw_value


def _iter_xml_text(root: ElementTree.Element, local_name: str) -> list[str]:
    return [node.text.strip() for node in root.iter() if _local_name(node.tag) == local_name and node.text and node.text.strip()]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]

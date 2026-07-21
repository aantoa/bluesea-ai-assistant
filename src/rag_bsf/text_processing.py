from __future__ import annotations

import re
from pathlib import Path

from rag_bsf.config import DEFAULT_CHUNK_CHARS, DEFAULT_CHUNK_OVERLAP, DOCUMENTS_DIR
from rag_bsf.document_loader import extract_front_matter, read_markdown
from rag_bsf.schemas import Chunk, DocumentRecord


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def clean_markdown(markdown: str) -> str:
    _, body = extract_front_matter(markdown)
    body = re.sub(r"!\[[^\]]*]\([^)]+\)", "", body)
    body = re.sub(r"\[([^\]]+)]\([^)]+\)", r"\1", body)
    body = re.sub(r"`([^`]+)`", r"\1", body)
    body = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", body)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def split_by_sections(text: str) -> list[tuple[str, str]]:
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [("Document", text)]

    sections: list[tuple[str, str]] = []
    preface = text[: matches[0].start()].strip()
    if preface:
        sections.append(("Preface", preface))

    for idx, match in enumerate(matches):
        section_title = match.group(2).strip()
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        sections.append((section_title, section_text))

    return sections


def split_long_text(
    text: str,
    target_chars: int = DEFAULT_CHUNK_CHARS,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    if len(text) <= target_chars:
        return [text]

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= target_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = _tail_overlap(current, overlap)

        if len(paragraph) > target_chars:
            chunks.extend(_split_by_window(paragraph, target_chars, overlap))
            current = ""
        else:
            current = f"{current}\n\n{paragraph}".strip() if current else paragraph

    if current:
        chunks.append(current)

    return [chunk.strip() for chunk in chunks if chunk.strip()]


def _tail_overlap(text: str, overlap: int) -> str:
    if overlap <= 0 or len(text) <= overlap:
        return ""
    return text[-overlap:].lstrip()


def _split_by_window(text: str, target_chars: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + target_chars, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_document(
    record: DocumentRecord,
    root_dir: Path = DOCUMENTS_DIR,
    target_chars: int = DEFAULT_CHUNK_CHARS,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Chunk]:
    path = root_dir / record.path
    clean_text = clean_markdown(read_markdown(path))
    chunks: list[Chunk] = []
    chunk_number = 1

    for section, section_text in split_by_sections(clean_text):
        for text in split_long_text(section_text, target_chars=target_chars, overlap=overlap):
            chunk_id = f"{record.document_id}::chunk-{chunk_number:04d}"
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=record.document_id,
                    text=text,
                    metadata={
                        "document_code": record.document_code,
                        "title": record.title,
                        "category": record.category,
                        "owner": record.owner,
                        "filename": record.filename,
                        "path": record.path,
                        "section": section,
                        "chunk_number": chunk_number,
                    },
                )
            )
            chunk_number += 1

    return chunks

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PROJECT_ROOT.parent if PROJECT_ROOT.name == "src" else PROJECT_ROOT
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
SOURCE_INVENTORY_FILE = DOCUMENTS_DIR / "inventory" / "BSF-INV-001_Document_Inventory.csv"
LEGACY_INVENTORY_FILE = DOCUMENTS_DIR / "inventory" / "document_inventory.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
INDEX_DIR = PROJECT_ROOT / "data" / "index"

CATEGORY_DIR_BY_NAME = {
    "corporate": "Corporate Documents",
    "hr": "Human Resources",
    "hse": "Health Safety and Environment",
    "inventory": "Document Control and Inventory",
    "it": "Information Technology",
    "operations": "Operations",
    "quality": "Quality and Certifications",
}

CATEGORY_DIR_BY_NAME = {
    category: folder for folder, category in CATEGORY_DIR_BY_NAME.items()
}

CATEGORY_DIR_BY_NAME.update(
    {
        "Corporate": "corporate",
        "Document Control": "inventory",
        "Human Resources": "hr",
        "HSE": "hse",
        "Operations": "operations",
        "Quality and Certifications": "quality",
        "Technology": "it",
    }
)


MARKDOWN_SOURCE_DIRS = tuple(DOCUMENTS_DIR / folder for folder in CATEGORY_DIR_BY_NAME)

INVENTORY_FILE = PROCESSED_DIR / "inventory.json"
CHUNKS_FILE = PROCESSED_DIR / "chunks.jsonl"
DOCUMENT_STATUS_FILE = PROCESSED_DIR / "document_status.csv"

VECTOR_INDEX_FILE = INDEX_DIR / "vectors.jsonl"
EMBEDDINGS_MANIFEST_FILE = INDEX_DIR / "embeddings_manifest.json"

DEFAULT_CHUNK_CHARS = 900
DEFAULT_CHUNK_OVERLAP = 150
DEFAULT_EMBEDDING_DIMENSIONS = 384
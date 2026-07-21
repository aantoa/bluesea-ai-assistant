import csv
from pathlib import Path

from rag_bsf import rag_pipeline


def test_validation_uses_declared_format_extension(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    inventory_dir = documents_dir / "inventory"
    corporate_dir = documents_dir / "Corporate"
    processed_dir = tmp_path / "processed"
    inventory_dir.mkdir(parents=True)
    corporate_dir.mkdir(parents=True)

    inventory_file = inventory_dir / "BSF-INV-001_Document_Inventory.csv"
    inventory_file.write_text(
        "\n".join(
            [
                "document_id,title,format,category,file_name",
                "BSF-CORP-001,Corporate Profile,PDF,Corporate,BSF-CORP-001_Corporate_Profile.docx",
            ]
        ),
        encoding="utf-8",
    )
    (corporate_dir / "BSF-CORP-001_Corporate_Profile.pdf").write_text("profile", encoding="utf-8")

    monkeypatch.setattr(rag_pipeline, "SOURCE_INVENTORY_FILE", inventory_file)
    monkeypatch.setattr(rag_pipeline, "DOCUMENT_STATUS_FILE", processed_dir / "document_status.csv")
    monkeypatch.setattr(rag_pipeline, "PROCESSED_DIR", processed_dir)

    stats = rag_pipeline.validate_document_collection(root_dir=documents_dir)

    status_rows = list(csv.DictReader((processed_dir / "document_status.csv").open(encoding="utf-8")))
    assert stats["source_available"] == 1
    assert stats["final_available"] == 1
    assert status_rows[0]["expected_file"] == "BSF-CORP-001_Corporate_Profile.pdf"
    assert status_rows[0]["matched_file"] == "BSF-CORP-001_Corporate_Profile.pdf"


def test_validation_uses_local_source_path_from_inventory(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    inventory_dir = documents_dir / "inventory"
    corporate_dir = documents_dir / "Corporate"
    processed_dir = tmp_path / "processed"
    inventory_dir.mkdir(parents=True)
    corporate_dir.mkdir(parents=True)

    inventory_file = inventory_dir / "BSF-INV-001_Document_Inventory.csv"
    inventory_file.write_text(
        "\n".join(
            [
                "document_id,title,format,category,file_name,local_source_path",
                "BSF-CORP-001,Corporate Profile,PDF,Corporate,BSF-CORP-001_Corporate_Profile.docx,Corporate/BSF-CORP-001_Corporate_Profile.pdf",
            ]
        ),
        encoding="utf-8",
    )
    (corporate_dir / "BSF-CORP-001_Corporate_Profile.pdf").write_text("profile", encoding="utf-8")

    monkeypatch.setattr(rag_pipeline, "SOURCE_INVENTORY_FILE", inventory_file)
    monkeypatch.setattr(rag_pipeline, "DOCUMENT_STATUS_FILE", processed_dir / "document_status.csv")
    monkeypatch.setattr(rag_pipeline, "PROCESSED_DIR", processed_dir)

    stats = rag_pipeline.validate_document_collection(root_dir=documents_dir)

    status_rows = list(csv.DictReader((processed_dir / "document_status.csv").open(encoding="utf-8")))
    assert stats["source_available"] == 1
    assert stats["final_available"] == 1
    assert status_rows[0]["expected_file"] == "BSF-CORP-001_Corporate_Profile.pdf"
    assert status_rows[0]["matched_file"] == "BSF-CORP-001_Corporate_Profile.pdf"


def test_validation_reports_wrong_declared_format_when_only_inventory_name_exists(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    inventory_dir = documents_dir / "inventory"
    corporate_dir = documents_dir / "corporate"
    processed_dir = tmp_path / "processed"
    inventory_dir.mkdir(parents=True)
    corporate_dir.mkdir(parents=True)

    inventory_file = inventory_dir / "BSF-INV-001_Document_Inventory.csv"
    inventory_file.write_text(
        "\n".join(
            [
                "document_id,title,format,category,file_name",
                "BSF-CORP-001,Corporate Profile,PDF,Corporate,BSF-CORP-001_Corporate_Profile.docx",
            ]
        ),
        encoding="utf-8",
    )
    (corporate_dir / "BSF-CORP-001_Corporate_Profile.docx").write_text("profile", encoding="utf-8")

    monkeypatch.setattr(rag_pipeline, "SOURCE_INVENTORY_FILE", inventory_file)
    monkeypatch.setattr(rag_pipeline, "DOCUMENT_STATUS_FILE", processed_dir / "document_status.csv")
    monkeypatch.setattr(rag_pipeline, "PROCESSED_DIR", processed_dir)

    stats = rag_pipeline.validate_document_collection(root_dir=documents_dir)

    status_rows = list(csv.DictReader((processed_dir / "document_status.csv").open(encoding="utf-8")))
    assert stats["source_available"] == 1
    assert stats["final_available"] == 0
    assert status_rows[0]["expected_file"] == "BSF-CORP-001_Corporate_Profile.pdf"
    assert status_rows[0]["matched_file"] == "BSF-CORP-001_Corporate_Profile.docx"
    assert status_rows[0]["status"] == "source_available_wrong_declared_format"


def test_processing_uses_same_flexible_inventory_match_as_validation(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    inventory_dir = documents_dir / "inventory"
    corporate_dir = documents_dir / "Corporate"
    processed_dir = tmp_path / "processed"
    inventory_dir.mkdir(parents=True)
    corporate_dir.mkdir(parents=True)

    inventory_file = inventory_dir / "BSF-INV-001_Document_Inventory.csv"
    inventory_file.write_text(
        "\n".join(
            [
                "document_id,title,format,category,file_name",
                "BSF-CORP-001,Corporate Profile,JSON,Corporate,BSF-CORP-001_Corporate_Profile.docx",
            ]
        ),
        encoding="utf-8",
    )
    (corporate_dir / "BSF-CORP-001_Corporate_Profile.json").write_text(
        '{"profile": "BlueSea Foods corporate profile"}',
        encoding="utf-8",
    )

    monkeypatch.setattr(rag_pipeline, "CHUNKS_FILE", processed_dir / "chunks.jsonl")
    monkeypatch.setattr(rag_pipeline, "INVENTORY_FILE", processed_dir / "inventory.json")
    monkeypatch.setattr(rag_pipeline, "PROCESSED_DIR", processed_dir)

    stats = rag_pipeline.process_documents(root_dir=documents_dir)

    assert stats["documents"] == 1
    assert stats["chunks"] == 1
    assert "BlueSea Foods corporate profile" in (processed_dir / "chunks.jsonl").read_text(encoding="utf-8")

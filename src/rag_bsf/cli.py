from __future__ import annotations

import argparse
import sys

from rag_bsf.rag_pipeline import build_inventory, process_documents, validate_document_collection


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BlueSea Foods document processing CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("inventory", help="Build document inventory from business-area Markdown folders.")
    subparsers.add_parser("validate-documents", help="Validate expected Ticket 1 files against documents folders.")
    subparsers.add_parser("process", help="Extract, clean and chunk business-area Markdown files.")

    args = parser.parse_args(argv)

    if args.command == "inventory":
        inventory = build_inventory()
        print(f"Inventory created with {len(inventory)} documents.")
        return 0

    if args.command == "validate-documents":
        stats = validate_document_collection()
        print(
            "Document validation completed: "
            f"{stats['final_available']}/{stats['expected']} final files, "
            f"{stats['markdown_available']}/{stats['expected']} Markdown files, "
            f"{stats['missing']} missing."
        )
        return 0

    if args.command == "process":
        stats = process_documents()
        print(
            "Processing completed: "
            f"{stats['documents']} documents, {stats['chunks']} chunks."
        )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

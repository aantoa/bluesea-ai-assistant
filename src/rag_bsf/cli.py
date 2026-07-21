from __future__ import annotations

import argparse
import sys

from rag_bsf.rag_pipeline import (
    build_inventory,
    index_chunks,
    process_documents,
    search_index,
    validate_document_collection,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BlueSea Foods document processing CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("inventory", help="Build document inventory from business-area Markdown folders.")
    subparsers.add_parser("validate-documents", help="Validate expected Ticket 1 files against documents folders.")
    subparsers.add_parser("process", help="Extract, clean and chunk business-area Markdown files.")
    subparsers.add_parser("index", help="Generate local embeddings and vector index from chunks.jsonl.")

    search_parser = subparsers.add_parser("search-index", help="Inspect nearest chunks from the local vector index.")
    search_parser.add_argument("question", help="Question or search text to compare against indexed chunks.")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of nearest chunks to show.")
    
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

    if args.command == "index":
        stats = index_chunks()
        print(
            "Indexing completed: "
            f"{stats['chunks']} chunks, {stats['vectors']} vectors, "
            f"{stats['dimensions']} dimensions, model {stats['embedding_model']}."
        )
        return 0

    if args.command == "search-index":
        results = search_index(args.question, top_k=args.top_k)
        if not results:
            print("No indexed chunks found. Generate chunks with local Markdown documents, then run `python -m rag_bsf.cli index`.")
            return 0
        for result in results:
            metadata = result.chunk.metadata
            print(
                f"[{result.source_label}] score={result.score:.3f} "
                f"{metadata.get('document_code', result.chunk.document_id)} - "
                f"{metadata.get('title', 'Untitled')} "
                f"section={metadata.get('section', 'N/A')}"
            )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
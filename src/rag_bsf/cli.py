from __future__ import annotations

import argparse
import sys

from rag_bsf.rag_pipeline import (
    answer_question,
    build_inventory,
    index_chunks,
    process_documents,
    retrieve_rag_context,
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
    
    retrieve_parser = subparsers.add_parser("retrieve", help="Retrieve reranked RAG context from the local vector index.")
    retrieve_parser.add_argument("question", help="Question to transform into retrieval context.")
    retrieve_parser.add_argument("--top-k", type=int, default=5, help="Number of final context chunks.")
    retrieve_parser.add_argument("--candidate-k", type=int, default=20, help="Number of semantic candidates before reranking.")
    retrieve_parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="Metadata filter in key=value form. Can be repeated, for example --filter category='Human Resources'.",
    )

    ask_parser = subparsers.add_parser("ask", help="Generate a grounded answer with citations from retrieved context.")
    ask_parser.add_argument("question", help="Question to answer using the local RAG index.")
    ask_parser.add_argument("--top-k", type=int, default=5, help="Number of final context chunks.")
    ask_parser.add_argument("--candidate-k", type=int, default=20, help="Number of semantic candidates before reranking.")
    ask_parser.add_argument("--min-confidence", type=float, default=0.18, help="Minimum retrieval score required to answer.")
    ask_parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="Metadata filter in key=value form. Can be repeated, for example --filter category='Human Resources'.",
    )

    args = parser.parse_args(argv)

    if args.command == "inventory":
        inventory = build_inventory()
        print(f"Inventory created with {len(inventory)} documents.")
        return 0

    if args.command == "validate-documents":
        stats = validate_document_collection()
        print(
            "Document validation completed: "
            f"{stats['source_available']}/{stats['expected']} source files, "
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

    if args.command == "retrieve":
        try:
            metadata_filters = _parse_metadata_filters(args.filter)
        except ValueError as exc:
            parser.error(str(exc))
        retrieved = retrieve_rag_context(
            args.question,
            top_k=args.top_k,
            candidate_k=args.candidate_k,
            metadata_filters=metadata_filters,
        )
        if not retrieved.results:
            print("No context chunks found. Check the vector index or relax metadata filters.")
            return 0

        filter_label = ", ".join(f"{key}={value}" for key, value in retrieved.applied_filters.items()) or "none"
        print(
            "Retrieval completed: "
            f"{retrieved.candidate_count} semantic candidates, "
            f"{retrieved.filtered_count} after filters, "
            f"{len(retrieved.results)} context chunks, filters={filter_label}."
        )
        print()
        print(retrieved.context)
        return 0

    if args.command == "ask":
        try:
            metadata_filters = _parse_metadata_filters(args.filter)
        except ValueError as exc:
            parser.error(str(exc))
        result = answer_question(
            args.question,
            top_k=args.top_k,
            candidate_k=args.candidate_k,
            metadata_filters=metadata_filters,
            min_confidence=args.min_confidence,
        )
        print(result.answer)
        if result.grounded:
            print()
            print("Referencias:")
            for source in result.sources:
                print(
                    f"- [{source.source_label}] {source.document_code} | "
                    f"{source.filename} | seccion={source.section} | "
                    f"owner={source.owner or 'N/A'}"
                )
        else:
            print()
            print(f"Fallback aplicado: {result.fallback_reason}")
        return 0

    return 1

def _parse_metadata_filters(raw_filters: list[str]) -> dict[str, str]:
    filters: dict[str, str] = {}
    for raw_filter in raw_filters:
        if "=" not in raw_filter:
            raise ValueError(f"Invalid metadata filter '{raw_filter}'. Use key=value.")
        key, value = raw_filter.split("=", 1)
        filters[key.strip()] = value.strip()
    return filters

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
# BlueSea AI Assistant

AI-powered corporate knowledge assistant for a fictional seafood company, developed as part of the Alura Agents Challenge.

The project implements a first local RAG pipeline in Python using BlueSea Foods corporate documents written in Markdown.

## Current Scope

This version covers the first two tickets:

- Ticket 1: document collection and organization.
- Ticket 2: content processing, text cleaning and chunking.

The next steps are embeddings, vector search improvements and answer generation with stronger citations.

## Repository Structure

```text
documents/
  inventory/
    document_inventory.csv
  raw/
    markdown/
rag_bsf/
scripts/
docs/
tests/
```

## Document Inventory

The source of truth for document ownership and metadata is:

```text
documents/inventory/document_inventory.csv
```

Place the Markdown source files in:

```text
documents/raw/markdown/
```

If the inventory lists an original file such as `employee_onboarding_guide.pdf`, the pipeline also accepts the Markdown equivalent `employee_onboarding_guide.md`.

## Commands

Build the inventory report:

```bash
python -m rag_bsf.cli inventory
```

Process documents, create chunks and build the local vector index:

```bash
python -m rag_bsf.cli ingest
```

Ask a question:

```bash
python -m rag_bsf.cli ask "What are the employee leave rules?"
```

## Local Prototype Decisions

- Markdown is the first supported source format.
- Metadata comes from `document_inventory.csv`.
- Embeddings use a deterministic local hashing model, so the first prototype can run without external APIs.
- If `OPENAI_API_KEY` is available, answer generation can use the OpenAI API; otherwise the CLI returns an extractive answer from the retrieved chunks.

## Documentation

- [Architecture](docs/architecture.md)
- [Ticket 1 - Recoleccion y organizacion documental](docs/tickets/01_recoleccion_organizacion.md)
- [Ticket 2 - Proceso y extraccion de contenido](docs/tickets/02_proceso_extraccion_contenido.md)
# Cierre tecnico del Ticket 03 - Indexacion vectorial

## Resumen

El Ticket 3 incorpora la capa de indexacion vectorial sobre los chunks generados en el Ticket 2.

La implementacion permite convertir cada fragmento limpio en un vector numerico local, guardar los vectores en un indice JSONL y registrar un manifest tecnico para trazabilidad.

## Entrada

```text
data/processed/chunks.jsonl
```

Este archivo proviene del Ticket 2 y contiene chunks con texto limpio y metadata documental.

## Proceso cerrado

1. Leer chunks desde `data/processed/chunks.jsonl`.
2. Generar embeddings locales mediante `HashingEmbedder`.
3. Normalizar vectores para comparacion por similitud coseno.
4. Guardar cada chunk y su vector en `data/index/vectors.jsonl`.
5. Generar `data/index/embeddings_manifest.json`.
6. Permitir inspeccion tecnica del indice con `search-index`.

## Salidas

```text
data/index/vectors.jsonl
data/index/embeddings_manifest.json
```

Estas salidas son locales y no deben subirse a GitHub.

## Archivos implementados o modificados

```text
src/rag_bsf/config.py
src/rag_bsf/embeddings.py
src/rag_bsf/vector_store.py
src/rag_bsf/schemas.py
src/rag_bsf/rag_pipeline.py
src/rag_bsf/cli.py
scripts/03_index.py
notebooks/03_ticket3_vector_index_colab.ipynb
tests/test_indexing.py
docs/tickets/03_indexacion_vectorial.md
docs/tickets/03_cierre_ticket_indexacion.md
```

## Validacion

Comandos de validacion:

```bash
PYTHONPATH=src python -m rag_bsf.cli index
PYTHONPATH=src python -m compileall src tests scripts
PYTHONPATH=src pytest
```

Si `chunks.jsonl` esta vacio, el comando de indexacion puede generar correctamente un indice con cero vectores. Eso no representa un error del codigo; solo indica que no hay chunks locales disponibles en esa ejecucion.

## Alcance no incluido

El Ticket 3 no implementa todavia:

- respuestas generadas por LLM;
- agente conversacional;
- citas en lenguaje natural;
- interfaz web;
- base vectorial externa;
- despliegue.
# Ticket 03 - Indexación vectorial

## Objetivo

Implementar la primera capa de indexacion vectorial del proyecto a partir de la salida generada en el Ticket 2.

La entrada principal del Ticket 3 es:

```text
data/processed/chunks.jsonl
```

Cada chunk se transforma en un vector numerico y se guarda junto con su texto original y metadata de trazabilidad.

## Alcance

El Ticket 3 cubre:

- lectura de chunks procesados;
- generacion de embeddings locales deterministicas;
- almacenamiento de vectores en un indice JSONL local;
- generacion de un manifest tecnico de indexacion;
- inspeccion basica de similitud contra el indice.

El Ticket 3 no cubre:

- uso de modelos comerciales de embeddings;
- base vectorial administrada externa;
- generacion de respuestas;
- agente conversacional;
- interfaz de usuario;
- despliegue.

## Diseño técnico

Para mantener el proyecto reproducible en local y en Colab, se implementa un modelo de embeddings local basado en hashing.

Este modelo no reemplaza un embedding comercial de produccion, pero permite validar el flujo de indexacion sin depender de credenciales, APIs externas ni infraestructura adicional.

## Flujo implementado

```text
data/processed/chunks.jsonl
  -> HashingEmbedder
  -> LocalVectorStore
  -> data/index/vectors.jsonl
  -> data/index/embeddings_manifest.json
```

## Componentes agregados

| Componente | Archivo | Funcion |
| --- | --- | --- |
| Embeddings locales | `src/rag_bsf/embeddings.py` | Convierte texto en vectores determinísticos normalizados. |
| Vector store local | `src/rag_bsf/vector_store.py` | Guarda y carga vectores en formato JSONL. |
| Pipeline de indexacion | `src/rag_bsf/rag_pipeline.py` | Lee chunks, genera vectores y escribe manifest. |
| CLI | `src/rag_bsf/cli.py` | Agrega comandos `index` y `search-index`. |
| Script Ticket 3 | `scripts/03_index.py` | Ejecuta la indexacion directamente. |
| Notebook Colab | `notebooks/03_ticket3_vector_index_colab.ipynb` | Ejecuta y documenta la indexacion en Google Colab. |
| Tests | `tests/test_indexing.py` | Valida embeddings, almacenamiento e indexacion. |

## Salidas locales

El Ticket 3 genera:

```text
data/index/vectors.jsonl
data/index/embeddings_manifest.json
```

`vectors.jsonl` contiene una linea por chunk indexado.

`embeddings_manifest.json` registra:

- archivo fuente de chunks;
- hash SHA-256 del archivo de chunks;
- modelo de embeddings usado;
- dimensiones del vector;
- cantidad de chunks;
- cantidad de vectores;
- fecha tecnica de generacion.

## Comandos

Indexar chunks:

```bash
PYTHONPATH=src python -m rag_bsf.cli index
```

Ejecutar script directo:

```bash
PYTHONPATH=src python scripts/03_index.py
```

Inspeccionar similitud del indice:

```bash
PYTHONPATH=src python -m rag_bsf.cli search-index "politica de reembolso de gastos"
```

## Criterio de cierre

El Ticket 3 queda cerrado tecnicamente cuando:

- `chunks.jsonl` puede leerse sin errores;
- cada chunk genera un vector;
- el indice local se guarda en `data/index/vectors.jsonl`;
- el manifest se guarda en `data/index/embeddings_manifest.json`;
- las pruebas unitarias pasan correctamente.
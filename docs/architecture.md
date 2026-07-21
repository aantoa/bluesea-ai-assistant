# Arquitectura por etapas para BlueSea Foods

## Objetivo

Construir progresivamente un asistente interno que responda preguntas de colaboradores usando documentos oficiales de BlueSea Foods.

El desarrollo se trabaja por tickets. La arquitectura debe crecer de forma incremental: cada ticket agrega componentes, comandos y salidas nuevas sin presentar como terminado lo que corresponde a etapas posteriores.

Al cierre del Ticket 3, el repositorio cubre:

- organizacion documental e inventario maestro;
- validacion local de documentos esperados;
- lectura de documentos Markdown disponibles;
- limpieza de contenido;
- division en chunks con metadata;
- exportacion de `data/processed/chunks.jsonl`;
- generacion de embeddings locales;
- almacenamiento de vectores en `data/index/vectors.jsonl`;
- generacion de manifest tecnico en `data/index/embeddings_manifest.json`.

## Arquitectura actual al cierre del Ticket 3

Esta arquitectura consolida lo cerrado en el Ticket 1, lo agregado en el Ticket 2 y la capa de indexacion del Ticket 3.

El Ticket 1 aporta:

- estructura documental por areas;
- inventario maestro;
- validacion de disponibilidad local;
- salidas de control documental.

El Ticket 2 agrega:

- lectura de documentos Markdown;
- extraccion de front matter cuando existe;
- cruce de cada documento con el inventario oficial;
- limpieza de texto;
- separacion por secciones;
- division en chunks;
- generacion de `chunks.jsonl` con metadata.

El Ticket 3 agrega:

- lectura de `chunks.jsonl`;
- generacion de embeddings locales deterministicas;
- normalizacion de vectores;
- almacenamiento local de vectores;
- generacion de manifest de indexacion;
- inspeccion tecnica de similitud contra el indice.

```text
documents/inventory/BSF-INV-001_Document_Inventory.csv
documents/<area>/*.md
  -> src/rag_bsf/document_loader.py
  -> src/rag_bsf/text_processing.py
  -> src/rag_bsf/rag_pipeline.py
  -> data/processed/document_status.csv
  -> data/processed/inventory.json
  -> data/processed/chunks.jsonl
  -> src/rag_bsf/embeddings.py
  -> src/rag_bsf/vector_store.py
  -> data/index/vectors.jsonl
  -> data/index/embeddings_manifest.json
```

El Ticket 2 procesa solo archivos Markdown disponibles localmente. El loader cruza cada archivo con el inventario oficial para completar metadata corporativa; luego el procesador limpia Markdown, conserva titulos y secciones utiles, y genera chunks con trazabilidad.

El Ticket 3 no genera respuestas, no implementa agente conversacional y no despliega una interfaz. Su entrega principal es dejar los chunks transformados en vectores consultables localmente.
## Detalle del Ticket 1

El Ticket 1 organiza la base documental del proyecto y valida que el inventario maestro pueda usarse como fuente oficial.

Entrada principal:

```text
documents/inventory/BSF-INV-001_Document_Inventory.csv
```

Proceso implementado:

1. Leer el inventario maestro.
2. Normalizar encabezados y campos principales.
3. Identificar codigo, categoria, responsable, estado y ruta esperada.
4. Validar si los archivos esperados existen localmente.
5. Generar salidas reproducibles en `data/processed/`.

Salidas del Ticket 1:

```text
data/processed/document_status.csv
data/processed/inventory.json
```

## Detalle del Ticket 2

El Ticket 2 incorpora la primera etapa de procesamiento de contenido del RAG. A partir de esta etapa, el sistema deja de trabajar solo con inventario documental y empieza a producir unidades de conocimiento reutilizables.

Entrada principal:

```text
documents/<area>/*.md
```

Entrada de metadata:

```text
documents/inventory/BSF-INV-001_Document_Inventory.csv
```

Proceso implementado:

1. Descubrir archivos Markdown en las carpetas documentales por area.
2. Leer el contenido del documento.
3. Extraer front matter si existe.
4. Identificar el codigo documental desde inventario, front matter o nombre de archivo.
5. Cruzar el documento con el inventario oficial.
6. Completar metadata corporativa: titulo, categoria, responsable, estado, version, confidencialidad, keywords y prioridad RAG.
7. Limpiar Markdown sin perder titulos ni contenido util.
8. Separar el documento por secciones.
9. Dividir textos largos en chunks.
10. Exportar cada chunk como una linea JSON independiente.

Salida principal:

```text
data/processed/chunks.jsonl
```

Cada registro de `chunks.jsonl` contiene:

```json
{
  "chunk_id": "BSF-CORP-001::1",
  "document_id": "BSF-CORP-001",
  "text": "Texto limpio del fragmento...",
  "metadata": {
    "document_code": "BSF-CORP-001",
    "title": "Corporate Profile",
    "category": "Corporate",
    "owner": "Corporate Affairs Manager",
    "confidentiality": "Internal Use",
    "section": "Overview",
    "chunk_number": 1,
    "chunk_total": 4
  }
}
```

## Detalle del Ticket 3

El Ticket 3 incorpora la indexacion vectorial local. A partir de esta etapa, el sistema ya puede transformar los chunks en vectores numericos y guardarlos en un indice reproducible.

Entrada principal:

```text
data/processed/chunks.jsonl
```

Proceso implementado:

1. Leer cada linea JSONL de `chunks.jsonl`.
2. Reconstruir el objeto `Chunk` con texto y metadata.
3. Generar un embedding local con `HashingEmbedder`.
4. Normalizar el vector para comparacion por similitud coseno.
5. Guardar chunk, vector, modelo y dimensiones en `vectors.jsonl`.
6. Registrar un manifest tecnico con hash del archivo fuente.

Salidas del Ticket 3:

```text
data/index/vectors.jsonl
data/index/embeddings_manifest.json
```

Cada registro de `vectors.jsonl` contiene:

```json
{
  "chunk": {
    "chunk_id": "BSF-CORP-001::chunk-0001",
    "document_id": "BSF-CORP-001",
    "text": "Texto limpio del fragmento...",
    "metadata": {
      "document_code": "BSF-CORP-001",
      "title": "Corporate Profile",
      "section": "Overview"
    }
  },
  "vector": [0.0, 0.12, -0.04],
  "embedding_model": "local-hashing-v1",
  "dimensions": 384
}
```

El modelo `local-hashing-v1` permite validar el pipeline sin depender de APIs externas. En una version productiva, esta capa podria reemplazarse por un modelo de embeddings especializado, manteniendo el mismo contrato de entrada y salida.

## Estructura documental actual

```text
documents/
  corporate/
  hr/
  hse/
  inventory/
    BSF-INV-001_Document_Inventory.csv
  it/
  operations/
  quality/
```

Los documentos fuente se mantienen fuera de GitHub. El repositorio versiona la estructura, el inventario maestro, el codigo de validacion y la documentacion del ticket.

## Flujo general implementado

1. Inventario documental: lee `documents/inventory/BSF-INV-001_Document_Inventory.csv` e identifica codigo, categoria, responsable, estado y disponibilidad local.
2. Validacion documental: cruza cada registro del inventario contra las carpetas por area bajo `documents/`.
3. Procesamiento: carga documentos Markdown disponibles, limpia texto y preserva titulos y secciones utiles.
4. Chunking: divide el contenido en fragmentos pequenos con metadata.
5. Exportacion de chunks: guarda `data/processed/chunks.jsonl`.
6. Embeddings: convierte cada chunk en un vector numerico local.
7. Indexacion vectorial: guarda chunks y vectores en `data/index/vectors.jsonl`.
8. Manifest: registra trazabilidad tecnica en `data/index/embeddings_manifest.json`.

## Alcance por ticket

| Ticket | Estado | Alcance |
| --- | --- | --- |
| Ticket 1 | Cerrado | Inventario, categorias, responsables, estructura documental y validacion local. |
| Ticket 2 | Cerrado tecnicamente | Carga Markdown, limpieza, extraccion de secciones y chunking con metadata. |
| Ticket 3 | Cerrado tecnicamente | Embeddings locales, indice vectorial JSONL y manifest de indexacion. |

La evidencia y los commits deben seguir este crecimiento. El Ticket 1 no incluye chunks; el Ticket 2 agrega chunks; el Ticket 3 agrega indexacion vectorial, pero no incluye agente ni interfaz.

## Componentes Python actuales

| Componente | Archivo | Responsabilidad actual |
| --- | --- | --- |
| Configuracion | `src/rag_bsf/config.py` | Centralizar rutas, inventario oficial, carpetas por area y salidas locales. |
| Esquemas | `src/rag_bsf/schemas.py` | Definir estructuras internas para documentos y chunks. |
| Loader | `src/rag_bsf/document_loader.py` | Leer inventario CSV, normalizar encabezados, extraer front matter y resolver metadata documental. |
| Processor | `src/rag_bsf/text_processing.py` | Limpiar texto Markdown, dividir por secciones y crear chunks con metadata. |
| Embeddings | `src/rag_bsf/embeddings.py` | Generar vectores locales determinísticos desde texto. |
| Vector store | `src/rag_bsf/vector_store.py` | Guardar, cargar e inspeccionar vectores locales. |
| Pipeline documental | `src/rag_bsf/rag_pipeline.py` | Validar documentos locales, generar inventario procesado, exportar chunks e indexar vectores. |
| CLI | `src/rag_bsf/cli.py` | Ejecutar comandos `validate-documents`, `inventory`, `process`, `index` y `search-index`. |

## Componentes de ejecucion

| Componente | Archivo | Responsabilidad actual |
| --- | --- | --- |
| Script Ticket 1 | `scripts/01_inventory.py` | Ejecutar inventario y validacion documental. |
| Script Ticket 2 | `scripts/02_process.py` | Procesar documentos Markdown y generar chunks. |
| Script Ticket 3 | `scripts/03_index.py` | Generar embeddings e indice vectorial local. |
| Notebook Ticket 1 | `notebooks/01_ticket1_inventory_validation_colab.ipynb` | Evidenciar validacion documental en Colab. |
| Notebook Ticket 2 | `notebooks/02_ticket2_processing_chunks_colab.ipynb` | Evidenciar procesamiento y chunking en Colab. |
| Notebook Ticket 3 | `notebooks/03_ticket3_vector_index_colab.ipynb` | Evidenciar indexacion vectorial local en Colab. |
| Tests Ticket 2 | `tests/test_text_processing.py` | Validar limpieza, separacion por secciones y chunking. |
| Tests Ticket 3 | `tests/test_indexing.py` | Validar embeddings, vector store e indexacion. |

## Salidas locales al cierre del Ticket 3

Las salidas reproducibles actuales se generan en `data/processed/`. Estas salidas son locales y no se suben a GitHub.

Ticket 1:

- `data/processed/document_status.csv`: estado de disponibilidad de cada documento esperado.
- `data/processed/inventory.json`: inventario maestro normalizado para uso posterior.

Ticket 2:

- `data/processed/chunks.jsonl`: fragmentos limpios con metadata.

Ticket 3:

- `data/index/vectors.jsonl`: chunks con vector numerico asociado.
- `data/index/embeddings_manifest.json`: manifest tecnico de indexacion.

## Metadata por chunk

Cada chunk conserva metadata suficiente para trazabilidad y citas futuras:

- `document_id`;
- `document_code`;
- `title`;
- `category`;
- `owner`;
- `backup_owner`;
- `status`;
- `version`;
- `confidentiality`;
- `access_level`;
- `format`;
- `keywords`;
- `rag_ingestion_priority`;
- `rag_content_type`;
- `metadata_quality_status`;
- `related_documents`;
- `review_date`;
- `filename`;
- `path`;
- `section`;
- `chunk_number`;
- `chunk_total`.

Esta metadata permite recuperar el origen de cada fragmento y mantener trazabilidad documental en las siguientes etapas del proyecto.

## Comandos validados

Validar documentos:

```bash
PYTHONPATH=src python -m rag_bsf.cli validate-documents
```

Generar inventario procesado:

```bash
PYTHONPATH=src python -m rag_bsf.cli inventory
```

Procesar documentos Markdown y generar chunks:

```bash
PYTHONPATH=src python -m rag_bsf.cli process
```

Generar embeddings e indice vectorial:

```bash
PYTHONPATH=src python -m rag_bsf.cli index
```

Inspeccionar el indice:

```bash
PYTHONPATH=src python -m rag_bsf.cli search-index "politica de reembolso de gastos"
```

Ejecucion directa del Ticket 2:

```bash
python scripts/02_process.py
```

Ejecucion directa del Ticket 3:

```bash
PYTHONPATH=src python scripts/03_index.py
```

## Metadata prevista para citas futuras

Todavía no forman parte del alcance cerrado:

- recuperación semántica;
- generación de respuestas con citas;
- agente de preguntas y respuestas.

Esta metadata se usara en tickets posteriores para recuperar contexto y citar fuentes en las respuestas.
# Arquitectura por etapas para BlueSea Foods

## Objetivo

Construir progresivamente un asistente interno que responda preguntas de colaboradores usando documentos oficiales de BlueSea Foods.

El desarrollo se trabaja por tickets. La arquitectura debe crecer de forma incremental: cada ticket agrega componentes, comandos y salidas nuevas sin presentar como terminado lo que corresponde a etapas posteriores.

Al cierre del Ticket 5, el repositorio cubre:

- organizacion documental e inventario maestro;
- validacion local de documentos esperados;
- lectura de documentos fuente disponibles en formatos soportados;
- limpieza de contenido;
- division en chunks con metadata;
- exportacion de `data/processed/chunks.jsonl`;
- generacion de embeddings locales;
- almacenamiento de vectores en `data/index/vectors.jsonl`;
- generacion de manifest tecnico en `data/index/embeddings_manifest.json`;
- recuperacion RAG local con busqueda semantica amplia;
- filtrado por metadata;
- reranking local;
- ensamblaje de contexto con fuentes;
- notebook del Ticket 4 preparado para ejecutar desde la raiz real del proyecto y usar `documents/` como fuente documental local;
- construccion de prompt restringido al contexto;
- generacion local de respuesta citada;
- validacion de confianza para reducir alucinaciones;
- fallback cuando no hay evidencia documental suficiente.

## Arquitectura actual al cierre del Ticket 5

Esta arquitectura consolida lo cerrado en el Ticket 1, lo agregado en el Ticket 2, la capa de indexacion del Ticket 3, la capa de recuperacion del Ticket 4 y la produccion controlada de respuestas del Ticket 5.

El Ticket 1 aporta:

- estructura documental por areas;
- inventario maestro;
- validacion de disponibilidad local;
- salidas de control documental.

El Ticket 2 agrega:

- extraccion multiformato de texto;
- extraccion de front matter cuando existe en Markdown;
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

El Ticket 4 agrega:

- transformacion de la pregunta en embedding usando el mismo modelo local;
- busqueda semantica amplia contra el indice vectorial;
- filtrado opcional por metadata;
- reranking deterministico de candidatos;
- ensamblaje de contexto con fuentes y metadata documental;
- validacion operativa del notebook para evitar ejecuciones desde copias equivocadas del proyecto;
- resolucion de `project_root`, `src/`, `PYTHONPATH` y `documents/` durante la ejecucion en Jupyter o Colab.

El Ticket 5 agrega:

- construccion de un prompt para LLM con instrucciones anti-alucinacion;
- generacion de respuesta basada solo en contexto recuperado;
- citas con etiquetas `[S1]`, `[S2]` vinculadas a archivo, seccion, categoria y responsable;
- umbral minimo de confianza antes de responder;
- fallback explicito cuando no se encuentra respaldo suficiente;
- salida estructurada `AnswerResult` para futuras interfaces.

```text
documents/inventory/BSF-INV-001_Document_Inventory.csv
documents/<area>/*.{md,pdf,docx,pptx,xlsx,html,json,csv,tsv,txt}
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
  -> src/rag_bsf/retrieval.py
  -> contexto RAG con fuentes
  -> src/rag_bsf/answer_generation.py
  -> respuesta final citada o fallback
```

El Ticket 2 procesa archivos fuente disponibles localmente. El loader cruza cada archivo con el inventario oficial para completar metadata corporativa; luego extrae texto segun formato, limpia marcas tecnicas, conserva titulos y secciones utiles, y genera chunks con trazabilidad.

El Ticket 5 no despliega una interfaz ni integra todavia un proveedor LLM externo. Su entrega principal es dejar el contrato de respuesta listo: prompt restringido, respuesta citada, fuentes estructuradas y fallback cuando los documentos no cubren la pregunta.

## Ejecucion del notebook Ticket 4

El notebook del Ticket 4 es una evidencia reproducible de la capa de recuperacion. Para evitar errores de rutas en Mac, Jupyter o Colab, su configuracion inicial resuelve la raiz del proyecto desde `pyproject.toml` y trabaja siempre desde esa carpeta.

Rutas esperadas:

```text
project_root/
  pyproject.toml
  src/
  documents/
    inventory/BSF-INV-001_Document_Inventory.csv
  data/
    processed/chunks.jsonl
    index/vectors.jsonl
```

La carpeta documental del notebook se define como:

```python
DOCUMENTS_DIR = project_root / "documents"
```

Los artefactos generados se mantienen separados:

```python
chunks_path = project_root / "data" / "processed" / "chunks.jsonl"
manifest_path = project_root / "data" / "index" / "embeddings_manifest.json"
vectors_path = project_root / "data" / "index" / "vectors.jsonl"
```

`DOCUMENTS_DIR` no debe apuntar a `chunks_path`, porque `chunks_path` es un archivo JSONL generado por el procesamiento del Ticket 2.

Como control operativo, el notebook detiene la ejecucion si detecta que `project_root` pertenece a `.Trash`. Esto evita usar copias vacias o equivocadas del proyecto.

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
documents/<area>/*.{md,pdf,docx,pptx,xlsx,html,json,csv,tsv,txt}
```

Entrada de metadata:

```text
documents/inventory/BSF-INV-001_Document_Inventory.csv
```

Proceso implementado:

1. Descubrir archivos soportados en las carpetas documentales por area.
2. Leer el contenido del documento.
3. Extraer front matter si existe.
4. Identificar el codigo documental desde inventario, front matter o nombre de archivo.
5. Cruzar el documento con el inventario oficial.
6. Completar metadata corporativa: titulo, categoria, responsable, estado, version, confidencialidad, keywords y prioridad RAG.
7. Limpiar marcas tecnicas sin perder titulos ni contenido util.
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

## Detalle del Ticket 4

El Ticket 4 incorpora la capa de recuperacion RAG. Esta etapa decide que fragmentos del indice vectorial deben entregarse al futuro LLM para generar una respuesta.

Entrada principal:

```text
data/index/vectors.jsonl
```

Proceso implementado:

1. Recibir una pregunta en lenguaje natural.
2. Transformar la pregunta en embedding con `HashingEmbedder`.
3. Buscar candidatos semanticamente cercanos en `LocalVectorStore`.
4. Aplicar filtros opcionales de metadata como `category`, `status` o `document_code`.
5. Expandir consultas frecuentes para cubrir sinonimos corporativos en el prototipo local.
6. Reordenar candidatos con un reranker local que combina similitud semantica y coincidencia lexical.
7. Retener los mejores fragmentos.
8. Ensamblar un bloque de contexto con etiquetas de fuente `[S1]`, `[S2]`, metadata y texto del chunk.

Comando principal:

```bash
PYTHONPATH=src python -m rag_bsf.cli retrieve "cuantos dias de vacaciones tengo" --candidate-k 20 --top-k 5
```

Ejemplo con filtro:

```bash
PYTHONPATH=src python -m rag_bsf.cli retrieve "licencia remunerada" --filter category="Human Resources"
```

Salida conceptual:

```text
[S1] BSF-HR-002 | Employee FAQ | section=Paid Leave | category=Human Resources | review_date=N/A
Texto recuperado del chunk...
```

La recuperacion queda separada de la generacion. Esto permite validar relevancia y trazabilidad antes de conectar un LLM.

## Detalle del Ticket 5

El Ticket 5 incorpora la capa de produccion y validacion de respuestas. Esta etapa recibe la pregunta original y el contexto recuperado por el Ticket 4.

Entrada principal:

```text
RetrievalContext
```

Proceso implementado:

1. Construir un prompt con la pregunta y el contexto recuperado.
2. Instruir al modelo a responder solo con base en el contexto.
3. Verificar si existen fuentes recuperadas.
4. Comparar el mejor score contra un umbral minimo de confianza.
5. Extraer frases soportadas por los chunks recuperados.
6. Citar cada afirmacion con la etiqueta de fuente correspondiente.
7. Adjuntar referencias con archivo, seccion, categoria y responsable.
8. Emitir fallback si no hay contexto, si el score es bajo o si no se encuentran frases soportadas.

Comando principal:

```bash
PYTHONPATH=src python -m rag_bsf.cli ask "cuantos dias de vacaciones tengo" --filter category="Human Resources"
```

Salida conceptual:

```text
Your entitlement depends on applicable law, employment conditions, and company policy. [S1]

Fuentes: [S1] BSF-HR-002_Employee_FAQ.md, seccion 8.2 How much annual leave do I have?.
```

Fallback conceptual:

```text
No encontre esta informacion en los documentos disponibles. Para evitar una respuesta incorrecta, no generare una conclusion sin respaldo documental.
```

La implementacion actual usa generacion extractiva local para mantener el proyecto reproducible sin APIs externas. En una version productiva, la funcion puede enviar el prompt a un LLM manteniendo el mismo contrato de entrada, salida, citas y fallback.

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
3. Procesamiento: carga documentos fuente disponibles, extrae texto por formato y preserva titulos y secciones utiles.
4. Chunking: divide el contenido en fragmentos pequenos con metadata.
5. Exportacion de chunks: guarda `data/processed/chunks.jsonl`.
6. Embeddings: convierte cada chunk en un vector numerico local.
7. Indexacion vectorial: guarda chunks y vectores en `data/index/vectors.jsonl`.
8. Manifest: registra trazabilidad tecnica en `data/index/embeddings_manifest.json`.
9. Recuperacion: transforma la pregunta en embedding, busca candidatos y aplica filtros.
10. Reranking: reordena candidatos con score combinado.
11. Contexto: arma el bloque textual con fuentes.
12. Prompt: combina pregunta, instrucciones y contexto recuperado.
13. Respuesta: genera una salida citada o fallback si no hay evidencia suficiente.

## Alcance por ticket

| Ticket | Estado | Alcance |
| --- | --- | --- |
| Ticket 1 | Cerrado | Inventario, categorias, responsables, estructura documental y validacion local. |
| Ticket 2 | Cerrado tecnicamente | Extraccion multiformato, limpieza, secciones y chunking con metadata. |
| Ticket 3 | Cerrado tecnicamente | Embeddings locales, indice vectorial JSONL y manifest de indexacion. |
| Ticket 4 | Cerrado tecnicamente | Recuperacion RAG local, filtros de metadata, reranking y ensamblaje de contexto. |
| Ticket 5 | Cerrado tecnicamente | Respuesta citada, prompt restringido, umbral de confianza y fallback anti-alucinacion. |

La evidencia y los commits deben seguir este crecimiento. El Ticket 1 no incluye chunks; el Ticket 2 agrega chunks; el Ticket 3 agrega indexacion vectorial; el Ticket 4 agrega recuperacion; el Ticket 5 agrega respuesta final controlada, pero no incluye interfaz ni deploy.

## Componentes Python actuales

| Componente | Archivo | Responsabilidad actual |
| --- | --- | --- |
| Configuracion | `src/rag_bsf/config.py` | Centralizar rutas, inventario oficial, carpetas por area y salidas locales. |
| Esquemas | `src/rag_bsf/schemas.py` | Definir estructuras internas para documentos y chunks. |
| Loader | `src/rag_bsf/document_loader.py` | Leer inventario CSV, normalizar encabezados, extraer front matter y resolver metadata documental. |
| Processor | `src/rag_bsf/text_processing.py` | Limpiar texto extraido, dividir por secciones y crear chunks con metadata. |
| Embeddings | `src/rag_bsf/embeddings.py` | Generar vectores locales determinísticos desde texto. |
| Vector store | `src/rag_bsf/vector_store.py` | Guardar, cargar e inspeccionar vectores locales. |
| Recuperacion | `src/rag_bsf/retrieval.py` | Recuperar, filtrar, rerankear y ensamblar contexto RAG. |
| Generacion de respuesta | `src/rag_bsf/answer_generation.py` | Construir prompt, validar evidencia, generar respuesta citada o fallback. |
| Pipeline documental | `src/rag_bsf/rag_pipeline.py` | Validar documentos locales, generar inventario procesado, exportar chunks e indexar vectores. |
| CLI | `src/rag_bsf/cli.py` | Ejecutar comandos `validate-documents`, `inventory`, `process`, `index`, `search-index`, `retrieve` y `ask`. |

## Componentes de ejecucion

| Componente | Archivo | Responsabilidad actual |
| --- | --- | --- |
| Script Ticket 1 | `scripts/01_inventory.py` | Ejecutar inventario y validacion documental. |
| Script Ticket 2 | `scripts/02_process.py` | Procesar documentos fuente y generar chunks. |
| Script Ticket 3 | `scripts/03_index.py` | Generar embeddings e indice vectorial local. |
| Script Ticket 4 | `scripts/04_retrieve.py` | Ejecutar recuperacion RAG local. |
| Script Ticket 5 | `scripts/05_answer.py` | Ejecutar una respuesta citada de ejemplo. |
| Notebook Ticket 1 | `notebooks/01_ticket1_inventory_validation_colab.ipynb` | Evidenciar validacion documental en Colab. |
| Notebook Ticket 2 | `notebooks/02_ticket2_processing_chunks_colab.ipynb` | Evidenciar procesamiento y chunking en Colab. |
| Notebook Ticket 3 | `notebooks/03_ticket3_vector_index_colab.ipynb` | Evidenciar indexacion vectorial local en Colab. |
| Notebook Ticket 4 | `notebooks/04_ticket4_retrieval_colab.ipynb` | Evidenciar recuperacion y ensamblaje de contexto en Colab. |
| Notebook Ticket 5 | `notebooks/05_ticket5_answer_generation_colab.ipynb` | Evidenciar respuesta citada, fuentes estructuradas y fallback anti-alucinacion en Colab. |
| Tests Ticket 2 | `tests/test_text_processing.py` | Validar limpieza, separacion por secciones y chunking. |
| Tests Ticket 3 | `tests/test_indexing.py` | Validar embeddings, vector store e indexacion. |
| Tests Ticket 4 | `tests/test_retrieval.py` | Validar filtros de metadata, reranking y armado de contexto. |

## Salidas locales al cierre del Ticket 4

Las salidas reproducibles actuales se generan en `data/processed/`. Estas salidas son locales y no se suben a GitHub.

Ticket 1:

- `data/processed/document_status.csv`: estado de disponibilidad de cada documento esperado.
- `data/processed/inventory.json`: inventario maestro normalizado para uso posterior.

Ticket 2:

- `data/processed/chunks.jsonl`: fragmentos limpios con metadata.

Ticket 3:

- `data/index/vectors.jsonl`: chunks con vector numerico asociado.
- `data/index/embeddings_manifest.json`: manifest tecnico de indexacion.

Ticket 4:

- contexto RAG generado en memoria desde `retrieve`.
- resultados con score semantico, score de reranking, etiqueta de fuente y metadata.

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

Procesar documentos fuente y generar chunks:

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

Recuperar contexto RAG:

```bash
PYTHONPATH=src python -m rag_bsf.cli retrieve "cuantos dias de vacaciones tengo"
```

Generar respuesta citada:

```bash
PYTHONPATH=src python -m rag_bsf.cli ask "cuantos dias de vacaciones tengo" --filter category="Human Resources"
```

Ejecucion directa del Ticket 2:

```bash
python scripts/02_process.py
```

Ejecucion directa del Ticket 3:

```bash
PYTHONPATH=src python scripts/03_index.py
```

Ejecucion directa del Ticket 5:

```bash
PYTHONPATH=src python scripts/05_answer.py
```

Evidencia en notebook del Ticket 5:

```text
notebooks/05_ticket5_answer_generation_colab.ipynb
```

## Metadata usada para citas

La metadata documental ya se usa en el Ticket 5 para citar fuentes en las respuestas finales. Cada fuente puede incluir codigo documental, archivo, titulo, seccion, categoria, responsable y score de recuperacion.

Todavia no forman parte del alcance cerrado la interfaz conversacional, la autenticacion y el deploy.

# Cierre tecnico del Ticket 04 - Recuperacion RAG

## Resumen

El Ticket 4 incorpora la capa de recuperacion sobre el indice vectorial generado en el Ticket 3 y deja preparado el contexto que se enviara al futuro LLM.

La implementacion permite convertir una pregunta en embedding, buscar candidatos semanticos, aplicar filtros de metadata, rerankear resultados y ensamblar un bloque de contexto con fuentes. Tambien se ajusto el notebook de Colab para trabajar correctamente con la carpeta real del proyecto y con los documentos locales ubicados en `documents/`.

## Entrada

```text
data/index/vectors.jsonl
```

Este archivo proviene del Ticket 3 y contiene chunks con texto, metadata y vectores.

Entradas locales requeridas para reprocesar desde cero:

```text
documents/inventory/BSF-INV-001_Document_Inventory.csv
documents/<area>/*
data/processed/chunks.jsonl
```

## Proceso cerrado

1. Recibir la pregunta del colaborador.
2. Generar el embedding de la pregunta con `HashingEmbedder`.
3. Buscar candidatos en `LocalVectorStore`.
4. Aplicar filtros opcionales por metadata.
5. Reordenar candidatos con reranking local.
6. Seleccionar los mejores fragmentos.
7. Ensamblar el contexto con etiquetas `[S1]`, `[S2]`, etc.
8. Validar la ejecucion del notebook desde la raiz real del proyecto.
9. Usar `documents/` como carpeta principal de documentos fuente.

## Salida

El Ticket 4 no genera un archivo persistente obligatorio. Su salida principal es un objeto `RetrievalContext` y un bloque textual de contexto listo para el futuro prompt del LLM.

Ejemplo conceptual:

```text
[S1] BSF-HR-002 | Employee FAQ | section=Paid Leave | category=Human Resources | review_date=N/A
Texto recuperado del chunk...
```

## Ajustes del notebook del Ticket 4

El notebook `notebooks/04_ticket4_retrieval_colab.ipynb` quedo preparado para evitar errores de ruta al ejecutarse en Mac, Jupyter o Colab.

La primera celda de rutas:

- detecta `project_root` usando `pyproject.toml`;
- cambia la carpeta de trabajo con `os.chdir(project_root)`;
- agrega `src/` a `sys.path`;
- exporta `PYTHONPATH` para que tambien funcionen comandos con `!python`;
- detiene la ejecucion si detecta una copia dentro de `.Trash`.

La carpeta de documentos se define explicitamente como:

```python
DOCUMENTS_DIR = project_root / "documents"
```

No debe definirse como:

```python
DOCUMENTS_DIR = chunks_path
```

porque `chunks_path` apunta al archivo generado:

```text
data/processed/chunks.jsonl
```

El notebook usa por defecto los documentos ya ubicados en la carpeta del proyecto:

```text
documents/
  inventory/BSF-INV-001_Document_Inventory.csv
  corporate/
  hr/
  hse/
  it/
  operations/
  quality/
```

Si Jupyter abre una copia equivocada del proyecto, se puede forzar temporalmente la ruta real con `PROJECT_ROOT_OVERRIDE`.

## Archivos implementados o modificados

```text
src/rag_bsf/config.py
src/rag_bsf/retrieval.py
src/rag_bsf/schemas.py
src/rag_bsf/rag_pipeline.py
src/rag_bsf/cli.py
scripts/04_retrieve.py
notebooks/04_ticket4_retrieval_colab.ipynb
tests/test_retrieval.py
docs/tickets/04_recuperacion_rag.md
docs/tickets/04_cierre_ticket_recuperacion.md
README.md
docs/architecture.md
```

## Validacion

Comandos de validacion:

```bash
PYTHONPATH=src python -m compileall src tests scripts
PYTHONPATH=src python -m rag_bsf.cli retrieve "cuantos dias de vacaciones tengo" --top-k 3 --candidate-k 20
PYTHONPATH=src pytest
```

Validacion esperada del notebook:

```text
PROJECT_ROOT = <ruta real del proyecto>
src agregado = <ruta real del proyecto>/src
Carpeta usada para documentos: <ruta real del proyecto>/documents
Inventario existe: True
```

Si `pytest` no esta instalado, se debe instalar en el entorno local o validar con los comandos Python anteriores hasta preparar el ambiente de pruebas.

## Alcance no incluido

El Ticket 4 no implementa todavia:

- generacion de respuestas con LLM;
- agente conversacional;
- interfaz web;
- citas redactadas en lenguaje natural;
- despliegue en OCI.

## Estado final

Ticket 04 cerrado tecnicamente. La recuperacion RAG local queda implementada, probada y documentada; el notebook queda preparado para ejecutar desde la carpeta real del proyecto usando `documents/` como fuente documental principal.

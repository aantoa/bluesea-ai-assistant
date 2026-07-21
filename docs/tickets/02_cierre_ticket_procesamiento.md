# Cierre del Ticket 2 - Procesamiento y generacion de chunks

## Proposito

Este archivo documenta el cierre tecnico del Ticket 2 del proyecto BlueSea AI Assistant. La finalidad de esta etapa es transformar documentos Markdown locales en fragmentos limpios, estructurados y trazables, listos para una etapa posterior de embeddings e indexacion vectorial.

El Ticket 2 no implementa embeddings, base vectorial, recuperacion semantica, agente conversacional ni interfaz. Esas funcionalidades quedan reservadas para tickets posteriores.

## Alcance del Ticket 2

El Ticket 2 cubre el procesamiento inicial de documentos Markdown ubicados en las carpetas documentales por area:

```text
documents/
  corporate/
  hr/
  hse/
  operations/
  quality/
  it/
  inventory/
```

Actividades incluidas:

- Descubrir archivos `.md` dentro de `documents/`.
- Leer contenido Markdown.
- Extraer front matter cuando exista.
- Cruzar cada documento con el inventario oficial.
- Usar el inventario como fuente principal de metadata.
- Limpiar Markdown sin perder titulos ni contenido util.
- Eliminar ruido basico de imagenes, links tecnicos, HTML, espacios duplicados y tablas vacias.
- Dividir documentos por secciones.
- Generar chunks de texto con metadata de trazabilidad.
- Exportar los chunks en formato JSONL.
- Dejar notebook de Colab como evidencia ejecutable del flujo.

## Archivos implementados

| Archivo | Proposito |
| --- | --- |
| `src/rag_bsf/document_loader.py` | Descubre documentos Markdown, extrae front matter y cruza metadata con el inventario. |
| `src/rag_bsf/text_processing.py` | Limpia texto Markdown, divide por secciones y genera chunks. |
| `src/rag_bsf/rag_pipeline.py` | Orquesta la funcion `process_documents()`. |
| `src/rag_bsf/schemas.py` | Define estructuras como `DocumentRecord` y `Chunk`. |
| `src/rag_bsf/cli.py` | Expone el comando `process`. |
| `scripts/02_process.py` | Ejecuta el procesamiento del Ticket 2 como script directo. |
| `notebooks/02_ticket2_processing_chunks_colab.ipynb` | Notebook de apoyo para ejecutar y evidenciar el flujo en Google Colab. |
| `tests/test_text_processing.py` | Pruebas minimas para limpieza, secciones y chunking. |

## Flujo tecnico

```text
documents/<area>/*.md
  -> document_loader.py
  -> text_processing.py
  -> rag_pipeline.process_documents()
  -> data/processed/chunks.jsonl
```

El inventario oficial usado como referencia es:

```text
documents/inventory/BSF-INV-001_Document_Inventory.csv
```

## Metadata generada por chunk

Cada chunk conserva metadata suficiente para rastrear su origen documental:

```text
document_id
document_code
title
category
owner
backup_owner
status
version
confidentiality
access_level
format
keywords
rag_ingestion_priority
rag_content_type
metadata_quality_status
related_documents
review_date
filename
path
section
chunk_number
chunk_total
```

Esta metadata sera necesaria en tickets posteriores para recuperar informacion, mostrar fuentes y controlar permisos o niveles de confidencialidad.

## Salida generada

La salida principal del Ticket 2 es:

```text
data/processed/chunks.jsonl
```

Cada linea del archivo representa un chunk independiente en formato JSON, con esta estructura general:

```json
{
  "chunk_id": "BSF-CORP-001::1",
  "document_id": "BSF-CORP-001",
  "text": "Contenido limpio del fragmento...",
  "metadata": {
    "document_code": "BSF-CORP-001",
    "title": "Corporate Profile",
    "category": "Corporate",
    "owner": "Corporate Affairs Manager",
    "section": "Overview",
    "chunk_number": 1
  }
}
```

## Comandos de validacion

Desde la raiz del repositorio:

```bash
PYTHONPATH=src python -m rag_bsf.cli validate-documents
PYTHONPATH=src python -m rag_bsf.cli inventory
PYTHONPATH=src python -m rag_bsf.cli process
PYTHONPATH=src python -m compileall -q src tests scripts
```

Tambien puede ejecutarse el script directo:

```bash
python scripts/02_process.py
```

## Resultado validado en este entorno

Validacion documental:

```text
Document validation completed: 0/24 final files, 0/24 Markdown files, 24 missing.
```

Inventario:

```text
Inventory created with 24 documents.
```

Procesamiento:

```text
Processing completed: 0 documents, 0 chunks.
```

Esta salida no representa un error del pipeline. En este entorno no estan disponibles los documentos Markdown locales dentro de `documents/<area>/`. Cuando los `.md` esten colocados localmente, el comando `process` debe generar los chunks correspondientes en `data/processed/chunks.jsonl`.

Compilacion:

```text
PYTHONPATH=src python -m compileall -q src tests scripts
```

El comando finalizo sin errores de sintaxis.

## Pruebas

Se dejaron pruebas minimas para validar:

- limpieza de Markdown;
- conservacion de titulos;
- division por secciones;
- generacion de multiples chunks para textos largos.

Archivo:

```text
tests/test_text_processing.py
```

En este entorno no se pudo ejecutar `pytest` porque no esta instalado:

```text
/bin/bash: line 1: pytest: command not found
```

Para ejecutarlo localmente:

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
```

## Notebook de Colab

El notebook oficial del Ticket 2 es:

```text
notebooks/02_ticket2_processing_chunks_colab.ipynb
```

El notebook permite:

- clonar o abrir el proyecto;
- instalar dependencias;
- validar el inventario;
- ejecutar el procesamiento;
- revisar `chunks.jsonl`;
- visualizar una tabla con los primeros chunks generados.

El notebook no reemplaza el codigo del paquete. La logica reutilizable queda en `src/rag_bsf/`.

## Criterio de cierre

El Ticket 2 se considera listo cuando:

- existe el comando `process`;
- los documentos Markdown pueden leerse desde `documents/<area>/`;
- el pipeline cruza cada documento con el inventario oficial;
- se genera `data/processed/chunks.jsonl`;
- cada chunk conserva texto limpio y metadata de trazabilidad;
- el notebook de Colab demuestra el flujo;
- las pruebas minimas quedan disponibles para validacion local.

## Pendiente para Ticket 3

El siguiente ticket debe iniciar la capa semantica del RAG:

- generar embeddings a partir de `chunks.jsonl`;
- definir el modelo de embeddings;
- construir o simular una base vectorial;
- guardar vectores e ids de chunks;
- validar busqueda por similitud;
- mantener trazabilidad hacia documento, seccion y chunk original.

## Commit sugerido

```bash
git add README.md docs/architecture.md docs/tickets/02_proceso_extraccion_contenido.md docs/tickets/02_cierre_ticket_procesamiento.md notebooks/02_ticket2_processing_chunks_colab.ipynb scripts/02_process.py tests src/rag_bsf
git commit -m "Add Markdown processing and chunk generation"
```

## Estado

Ticket 2 listo para cierre tecnico, condicionado a ejecutar el procesamiento con los documentos Markdown locales disponibles en la maquina o en Google Colab.
# Ticket 2 - Proceso y extraccion de contenido

## Objetivo

Transformar los documentos Markdown oficiales en texto limpio, estructurado y segmentado, listo para generar embeddings e indexar.

## Alcance inicial

El inicio del Ticket 2 se concentra solo en documentos `.md`, porque BlueSea Foods esta construyendo su base documental en Markdown.

Este ticket no incluye embeddings, base vectorial, recuperacion ni generacion de respuestas. Esas etapas deben desarrollarse en tickets posteriores.

## Checklist tecnico

- Crear loader de documentos Markdown desde las carpetas de negocio en `documents/`.
- Cruzar cada Markdown con `documents/inventory/document_inventory.csv`.
- Detectar codigo documental desde el inventario, front matter o nombre del archivo.
- Asociar categoria, responsable, version, estado, confidencialidad y fechas desde el inventario.
- Extraer front matter cuando exista.
- Limpiar sintaxis Markdown sin perder titulos.
- Eliminar ruido basico: espacios duplicados, imagenes, links tecnicos y tablas vacias.
- Dividir documentos por secciones y chunks.
- Agregar metadata a cada chunk.
- Exportar inventario documental.
- Exportar chunks procesados.
- Validar que cada chunk conserve fuente y seccion.

## Resultado esperado

Archivos procesados en `data/processed/`:

- `inventory.json`: inventario documental.
- `chunks.jsonl`: fragmentos limpios con metadata.

## Comandos

Generar reporte del inventario:

```bash
python -m rag_bsf.cli inventory
```

Procesar documentos Markdown:

```bash
python -m rag_bsf.cli process
```

## Criterio para avanzar al siguiente ticket

El Ticket 2 se considera listo cuando:

- Exista al menos un conjunto inicial de documentos Markdown cargado desde el Ticket 1.
- `data/processed/chunks.jsonl` contenga fragmentos limpios y con metadata.
- Cada chunk conserve `document_code`, `title`, `category`, `owner`, `filename`, `path`, `section` y `chunk_number`.
- Se hayan revisado manualmente algunos chunks para confirmar que el texto no perdio sentido.
# Arquitectura por etapas para BlueSea Foods

## Objetivo

Construir progresivamente un asistente interno que responda preguntas de colaboradores usando documentos oficiales de BlueSea Foods.

El desarrollo se trabajara por tickets. En este momento el repositorio cubre el Ticket 1: organizacion, inventario y validacion local de la coleccion documental.

## Arquitectura actual del Ticket 1

```text
documents/inventory/BSF-INV-001_Document_Inventory.csv
  -> src/rag_bsf/document_loader.py
  -> src/rag_bsf/rag_pipeline.py
  -> data/processed/document_status.csv
  -> data/processed/inventory.json
```

El Ticket 1 no procesa contenido interno de los documentos. Solo valida que el inventario maestro pueda leerse y que los archivos esperados existan localmente en las carpetas definidas.

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

## Flujo general previsto

1. Inventario documental: lee `documents/inventory/BSF-INV-001_Document_Inventory.csv` e identifica codigo, categoria, responsable, estado y disponibilidad local.
2. Validacion documental: cruza cada registro del inventario contra las carpetas por area bajo `documents/`.
3. Procesamiento: carga documentos Markdown disponibles, limpia texto y preserva titulos y secciones utiles.
4. Chunking: divide el contenido en fragmentos pequenos con metadata.
5. Embeddings: convierte cada fragmento en un vector numerico comparable.
6. Base vectorial: guarda chunks y vectores para consulta.
7. Recuperacion: compara la pregunta contra los vectores y trae los fragmentos mas cercanos.
8. Generacion: redacta una respuesta usando solo el contexto recuperado y agrega citas.

## Alcance por ticket

| Ticket | Estado | Alcance |
| --- | --- | --- |
| Ticket 1 | En cierre | Inventario, categorias, responsables, estructura documental y validacion local. |
| Ticket 2 | Pendiente | Carga Markdown, limpieza, extraccion de secciones y chunking. |
| Ticket 3+ | Pendiente | Embeddings, base vectorial, recuperacion y generacion. |

## Componentes Python

| Componente | Archivo | Responsabilidad |
| --- | --- | --- |
| Configuracion | `src/rag_bsf/config.py` | Centralizar rutas, inventario oficial, carpetas por area y salidas locales. |
| Esquemas | `src/rag_bsf/schemas.py` | Definir las estructuras internas para documentos y chunks futuros. |
| Loader | `src/rag_bsf/document_loader.py` | Leer el inventario CSV, normalizar encabezados y resolver rutas documentales. |
| Pipeline documental | `src/rag_bsf/rag_pipeline.py` | Validar documentos locales y generar el inventario procesado. |
| CLI | `src/rag_bsf/cli.py` | Ejecutar comandos de validacion e inventario por terminal. |
| Processor | `src/rag_bsf/text_processing.py` | Limpiar texto y dividirlo en chunks; se usara desde el Ticket 2. |

## Salidas locales del Ticket 1

La validacion genera archivos reproducibles en `data/processed/`. Esta carpeta es salida local y no se sube a GitHub.

- `document_status.csv`: estado de disponibilidad de cada documento esperado.
- `inventory.json`: inventario maestro normalizado para uso posterior.

## Metadata prevista para citas futuras

Cada chunk conserva:

- archivo original;
- codigo documental;
- categoria;
- responsable;
- seccion;
- numero de chunk;
- ruta relativa.

Esta metadata se usara en tickets posteriores para recuperar contexto y citar fuentes en las respuestas.
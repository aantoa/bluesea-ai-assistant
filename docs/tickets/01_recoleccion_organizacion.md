# Ticket 1 - Recoleccion y organizacion documental

## Objetivo

Mapear, organizar y validar los documentos que alimentaran el sistema RAG de BlueSea Foods antes de iniciar el procesamiento tecnico.

## Estado actual

El Ticket 1 esta parcialmente listo. El repositorio ya tiene la estructura documental y el inventario maestro, pero falta colocar los documentos Markdown oficiales dentro de las carpetas por area.

## Checklist de validacion

| Item | Estado | Evidencia |
| --- | --- | --- |
| Mapear fuentes documentales simuladas | Listo | `documents/inventory/document_inventory.csv` incluye la fuente de cada documento. |
| Definir categorias de negocio | Listo | Carpetas en `documents/`: `commercial`, `finance`, `hr`, `hse`, `it`, `legal`, `operations`, `quality`. |
| Definir criterios de curaduria | Pendiente | Falta documentar reglas de version oficial, borradores, duplicados y documentos excluidos. |
| Asignar responsables por categoria | Listo inicial | El CSV tiene columna `owner`. |
| Definir acceso y permisos | Listo inicial | El CSV tiene `confidentiality`; en esta etapa el agente solo requiere lectura. |
| Definir proceso de ingesta inicial | Listo inicial | Se usaran Markdown por area y el CSV como metadata oficial. |
| Elaborar inventario documental | Listo inicial | `documents/inventory/document_inventory.csv`. |
| Crear documentos ficticios | Pendiente | Aun no hay archivos `.md` en las carpetas de negocio. |
| Validar formatos y consistencia | Pendiente | Depende de que los `.md` esten cargados. |
| Organizar estructura documental | Listo | Carpetas por area creadas. |
| Documentar resultado en el repositorio | En avance | Este archivo documenta el estado del ticket. |

## Resultado esperado

Una carpeta documental controlada, con archivos oficiales, categoria asignada, responsable definido y convencion de nombres consistente.

En el repositorio, la fuente oficial de esta etapa es:

- `documents/inventory/document_inventory.csv`: inventario maestro.
- `documents/commercial/`, `documents/finance/`, `documents/hr/`, `documents/hse/`, `documents/it/`, `documents/legal/`, `documents/operations/`, `documents/quality/`: documentos Markdown disponibles para ingesta, organizados por area.

El comando `python -m rag_bsf.cli inventory` genera `data/processed/inventory.json` marcando que documentos del inventario ya tienen archivo Markdown disponible.

## Criterio para cerrar el Ticket 1

El Ticket 1 se considera cerrado cuando:

- Todos los documentos definidos en el inventario tengan su version Markdown oficial en la carpeta de area correspondiente.
- El comando `python -m rag_bsf.cli inventory` marque `markdown_available=true` para los documentos que formaran parte de la primera ingesta.
- Los documentos tengan una convencion de nombres consistente, idealmente incluyendo el codigo documental, por ejemplo `BSF-HR-002_Employee_FAQ.md`.
- No existan borradores, duplicados o documentos fuera de categoria dentro de `documents/`.
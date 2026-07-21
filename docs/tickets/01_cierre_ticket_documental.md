# Cierre del Ticket 1 - Colecta y organizacion de documentos

## Proposito

Este archivo documenta el cierre organizacional del Ticket 1 del proyecto BlueSea AI Assistant. La finalidad de esta etapa es dejar definida y controlada la coleccion documental que servira como base para el agente inteligente corporativo.

El proyecto simula una empresa del sector seafood llamada BlueSea Foods, con documentos internos distribuidos por areas. Estos documentos seran usados posteriormente para construir un agente de IA capaz de responder preguntas sobre politicas, operaciones, calidad, seguridad, tecnologia y control documental.

## Alcance del Ticket 1

El Ticket 1 cubre unicamente la colecta, clasificacion y organizacion documental. No incluye procesamiento de texto, embeddings, base vectorial, agente conversacional ni despliegue en la nube.

Actividades incluidas:

- Definir las areas documentales del proyecto.
- Crear la estructura de carpetas.
- Elaborar la lista final de documentos.
- Asignar codigo, nombre, formato y carpeta destino.
- Mantener los documentos fuente fuera de GitHub.
- Dejar un criterio claro para validar que la coleccion documental esta completa.

## Estructura documental definida

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

## Lista final de documentos

| Area | Codigo | Documento | Formato final | Carpeta |
| --- | --- | --- | --- | --- |
| Documentos corporativos | BSF-CORP-001 | Corporate Profile | PDF | documents/corporate/ |
| Documentos corporativos | BSF-CORP-002 | Corporate Glossary | PDF | documents/corporate/ |
| Documentos corporativos | BSF-DOC-STD-001 | Corporate Document Standard | PDF | documents/corporate/ |
| Documentos corporativos | BSF-CORP-003 | Corporate Organization Chart | PDF | documents/corporate/ |
| Documentos corporativos | BSF-CORP-004 | Corporate Knowledge Map | PDF | documents/corporate/ |
| Recursos Humanos | BSF-HR-001 | Employee Onboarding Guide | PDF | documents/hr/ |
| Recursos Humanos | BSF-HR-002 | Employee FAQ | Markdown | documents/hr/ |
| Recursos Humanos | BSF-HR-003 | Leave and Benefits Policy | DOCX | documents/hr/ |
| Seguridad, Salud y Medio Ambiente | BSF-HSE-001 | Workplace Safety Procedure | DOCX | documents/hse/ |
| Seguridad, Salud y Medio Ambiente | BSF-HSE-002 | Emergency Response Guide | PDF | documents/hse/ |
| Operaciones | BSF-OPS-001 | Cold Chain Control Register | XLSX | documents/operations/ |
| Operaciones | BSF-OPS-002 | Authorized Fishing Vessels | CSV | documents/operations/ |
| Operaciones | BSF-OPS-003 | Seafood Species Catalog | JSON | documents/operations/ |
| Operaciones | BSF-OPS-004 | Seafood Receiving and Inspection Procedure | PDF | documents/operations/ |
| Calidad y certificaciones | BSF-QMS-001 | Quality Management Induction | PPTX | documents/quality/ |
| Calidad y certificaciones | BSF-QMS-002 | Certification and Compliance Overview | PDF | documents/quality/ |
| Calidad y certificaciones | BSF-QMS-003 | Corrective Action and Nonconformity Procedure | PDF | documents/quality/ |
| Tecnologia | BSF-IT-001 | BlueTrack User Manual | HTML | documents/it/ |
| Tecnologia | BSF-IT-002 | Corporate Systems Access Guide | PDF | documents/it/ |
| Control e inventario documental | BSF-INV-001 | Document Inventory | CSV | documents/inventory/ |
| Control e inventario documental | BSF-INV-002 | Document Ownership Matrix | XLSX | documents/inventory/ |
| Control e inventario documental | BSF-INV-003 | Document Sources and Ingestion Plan | Markdown | documents/inventory/ |
| Control e inventario documental | BSF-INV-004 | Document Curation and Quality Criteria | Markdown | documents/inventory/ |
| Control e inventario documental | BSF-INV-005 | Access and Permissions Policy | Markdown | documents/inventory/ |

## Resumen por formato

| Formato | Cantidad |
| --- | ---: |
| PDF | 11 |
| DOCX | 2 |
| XLSX | 2 |
| PPTX | 1 |
| Markdown | 4 |
| CSV | 2 |
| JSON | 1 |
| HTML | 1 |
| **Total** | **24** |

## Documentos de calidad y certificaciones

El bloque de calidad y certificaciones debe considerar referencias a los siguientes marcos, normas o esquemas:

- ISO 9001
- SMETA
- HACCP
- BRCGS Food Safety
- MSC Chain of Custody
- BASC
- IFS Food

## Politica de versionamiento

Los documentos fuente no se suben a GitHub. El repositorio conserva solamente la estructura, el codigo, la documentacion tecnica y los archivos necesarios para demostrar la organizacion del proyecto.

La regla de privacidad es:

```text
Los documentos fuente se mantienen localmente y no se versionan por contener informacion interna o simulada de uso privado. El repositorio conserva la estructura, el inventario y el pipeline de procesamiento.
```

Por ese motivo, `.gitignore` debe ignorar los documentos dentro de `documents/`, conservando unicamente las carpetas mediante archivos `.gitkeep`.

## Evidencia esperada

Para validar el cierre del Ticket 1, se debe ejecutar desde la raiz del repositorio:

```bash
python -m rag_bsf.cli validate-documents
```

El comando debe confirmar que los 24 documentos finales existen localmente en sus carpetas correspondientes.

## Criterio de cierre

El Ticket 1 se considera cumplido cuando:

- La estructura `documents/` contiene las siete areas definidas.
- Los 24 documentos existen localmente en la carpeta correspondiente.
- El inventario documental contiene codigo, nombre, area, formato, responsable y estado.
- Los documentos fuente estan protegidos por `.gitignore` y no se suben a GitHub.
- El repositorio conserva evidencia documental suficiente para explicar el alcance del challenge.
- El proyecto queda listo para iniciar el Ticket 2: procesamiento, limpieza y chunking.

## Estado

Ticket 1 listo para cierre organizacional, condicionado a que los 24 documentos esten disponibles localmente y que GitHub conserve solo la estructura y documentacion del proyecto.
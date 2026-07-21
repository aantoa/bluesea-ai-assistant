# BlueSea AI Assistant

Proyecto para el Challenge de Agentes de IA de Alura. La solucion simula un asistente corporativo para **BlueSea Foods**, una empresa ficticia del sector seafood que necesita consultar informacion interna sin revisar manualmente documentos, politicas, guias y registros.

La solucion final sera un agente RAG capaz de responder preguntas en lenguaje natural usando la documentacion corporativa como fuente. El proyecto se esta desarrollando por tickets para avanzar de forma ordenada: primero documentacion, luego procesamiento, despues recuperacion semantica, agente y deploy.

## Estado Actual

| Ticket | Estado | Que contiene |
| --- | --- | --- |
| Ticket 1 | Cerrado | Estructura de carpetas, inventario maestro de 24 documentos, criterio de privacidad y validador local. |
| Ticket 2 | Cerrado tecnicamente | Lectura de documentos Markdown, limpieza de texto y generacion de chunks con metadata. |
| Ticket 3 | Cerrado tecnicamente | Generacion de embeddings locales, indice vectorial JSONL y manifest de indexacion. |
| Ticket 4+ | Pendiente | Recuperacion RAG, generacion de respuestas, interfaz y deploy en OCI. |

> El repositorio todavia no contiene el agente conversacional completo. La version actual crece por tickets: Ticket 1 prepara y valida la base documental; Ticket 2 agrega el procesamiento Markdown y la generacion de chunks; Ticket 3 agrega la indexacion vectorial local.

## Documentacion Definida

BlueSea Foods trabaja con 24 documentos internos, organizados por area:

| Area | Cantidad |
| --- | ---: |
| Documentos corporativos | 5 |
| Recursos Humanos | 3 |
| Seguridad, Salud y Medio Ambiente | 2 |
| Operaciones | 4 |
| Calidad y certificaciones | 3 |
| Tecnologia | 2 |
| Control e inventario documental | 5 |
| **Total** | **24** |

Conteo por formato:

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

Inventario maestro:

```text
documents/inventory/BSF-INV-001_Document_Inventory.csv
```

Documentos de cierre:

```text
docs/tickets/01_cierre_ticket_documental.md
docs/tickets/02_cierre_ticket_procesamiento.md
docs/tickets/03_cierre_ticket_indexacion.md
```

## Privacidad y GitHub

Los documentos fuente completos se mantienen **localmente** y no se suben a GitHub. Esto evita publicar archivos internos o simulados del caso corporativo.

GitHub debe contener:

- codigo fuente del proyecto;
- README y documentacion tecnica;
- tickets del proyecto;
- notebook de Colab;
- inventario maestro;
- estructura de carpetas mediante `.gitkeep`.

GitHub no debe contener:

- PDF;
- DOCX;
- XLSX;
- PPTX;
- HTML;
- JSON;
- CSV operativos distintos al inventario maestro;
- Markdown internos usados como documentos fuente.

La regla esta configurada en `.gitignore`:

```gitignore
documents/**/*
!documents/**/
!documents/**/.gitkeep
!documents/inventory/BSF-INV-001_Document_Inventory.csv
```

## Estructura del Repositorio

```text
bluesea-ai-assistant/
  assets/
    .gitkeep
  data/
    processed/              
  docs/
    architecture.md
    tickets/
      01_recoleccion_organizacion.md
      01_cierre_ticket_documental.md
      02_proceso_extraccion_contenido.md
      02_cierre_ticket_procesamiento.md
      03_indexacion_vectorial.md
      03_cierre_ticket_indexacion.md
  documents/
    corporate/
    hr/
    hse/
    inventory/
      BSF-INV-001_Document_Inventory.csv
    it/
    operations/
    quality/
  notebooks/
    01_ticket1_inventory_validation_colab.ipynb
    02_ticket2_processing_chunks_colab.ipynb
    03_ticket3_vector_index_colab.ipynb
  scripts/
    01_inventory.py
    02_process.py              # Ticket 2; no se usa para cerrar el Ticket 1
    03_index.py                # Ticket 3; genera indice vectorial local
  src/
    rag_bsf/
      __init__.py
      cli.py
      config.py
      document_loader.py
      embeddings.py
      rag_pipeline.py
      schemas.py
      text_processing.py
      vector_store.py
  tests/
    conftest.py
    test_indexing.py
    test_text_processing.py
  .gitignore
  pyproject.toml
  requirements.txt
  README.md
```

La estructura anterior con `documents/raw/markdown/`, `rag_bsf/` en la raiz o `document_inventory.csv` ya no corresponde a esta version. El codigo versionado vive en `src/rag_bsf/` y los documentos fuente se organizan localmente por area dentro de `documents/`.

## Requisitos

El proyecto requiere:

```text
Python >= 3.10
```

Recomendacion practica:

- usar Python 3.11 si quieres maxima estabilidad para futuras librerias de IA;
- Python 3.14 puede funcionar para esta etapa actual;
- no usar Python 3.9, porque el proyecto no lo acepta.

Si al instalar aparece un error como:

```text
Package 'bluesea-ai-assistant' requires a different Python: 3.9.6 not in '>=3.10'
```

significa que tu `.venv` fue creado con Python 3.9. Debes recrearlo con Python 3.10 o superior.

## Instalacion Local

Desde la raiz del proyecto:

```bash
python --version
```

Si muestra Python 3.10 o superior:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

En Mac, si tienes Python 3.14:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python --version
pip install --upgrade pip
pip install -r requirements.txt
```

Si prefieres Python 3.11:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python --version
pip install --upgrade pip
pip install -r requirements.txt
```

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Comandos Principales del Ticket 1

Validar que los documentos esperados del Ticket 1 existan localmente:

```bash
python -m rag_bsf.cli validate-documents
```

Generar inventario tecnico de documentos Markdown disponibles:

```bash
python -m rag_bsf.cli inventory
```

Si aun no instalaste el paquete, puedes ejecutar temporalmente con `PYTHONPATH=src`:

```bash
PYTHONPATH=src python -m rag_bsf.cli validate-documents
PYTHONPATH=src python -m rag_bsf.cli inventory
```

Las salidas se generan en:

```text
data/processed/
```

Esos archivos son resultados locales de ejecucion y no se suben a GitHub.

## Comandos Principales del Ticket 2

Procesar documentos Markdown locales y generar chunks:

```bash
PYTHONPATH=src python -m rag_bsf.cli process
```

Tambien puedes usar el script directo:

```bash
python scripts/02_process.py
```

La salida principal del Ticket 2 es:

```text
data/processed/chunks.jsonl
```

Cada linea de `chunks.jsonl` contiene un fragmento limpio con texto y metadata de trazabilidad: `document_code`, `title`, `category`, `owner`, `filename`, `path`, `section`, `chunk_number`, `confidentiality`, `status` y `review_date`.

Si no tienes documentos `.md` locales en `documents/`, el comando puede terminar correctamente con:

```text
Processing completed: 0 documents, 0 chunks.
```

Eso no es error de codigo; significa que todavia no hay Markdown disponible para ingesta.

## Comandos Principales del Ticket 3

Generar embeddings locales e indice vectorial desde `chunks.jsonl`:

```bash
PYTHONPATH=src python -m rag_bsf.cli index
```

Tambien puedes usar el script directo:

```bash
PYTHONPATH=src python scripts/03_index.py
```

Las salidas principales del Ticket 3 son:

```text
data/index/vectors.jsonl
data/index/embeddings_manifest.json
```

Para inspeccionar tecnicamente el indice:

```bash
PYTHONPATH=src python -m rag_bsf.cli search-index "politica de reembolso de gastos"
```

Este comando solo muestra chunks cercanos y sus scores. Todavia no genera una respuesta final ni reemplaza al agente RAG.

## Resultado Esperado de Validacion

Si solo tienes el repositorio clonado desde GitHub, es normal que el validador muestre pocos documentos disponibles, porque los documentos fuente no se versionan.

Ejemplo esperado en un repositorio sin documentos locales:

```text
Document validation completed: 0/24 final files, 0/24 Markdown files, 24 missing.
```

Ese resultado es normal si solo esta versionado el inventario y los documentos fuente finales se mantienen fuera de GitHub.

Para cerrar el Ticket 1 en tu maquina, debes tener los 24 documentos colocados localmente en sus carpetas. En ese caso, el validador debe acercarse a:

```text
Document validation completed: 24/24 final files, ... Markdown files, 0 missing.
```

El numero de Markdown depende de cuantos documentos hayan sido convertidos o preparados para ingesta.

## Uso en Google Colab

El proyecto incluye notebooks separados por ticket. El Ticket 1 usa Colab como evidencia de validacion documental; el Ticket 2 usa Colab como laboratorio de procesamiento; el Ticket 3 usa Colab como laboratorio de indexacion vectorial local.

```text
notebooks/01_ticket1_inventory_validation_colab.ipynb
notebooks/02_ticket2_processing_chunks_colab.ipynb
notebooks/03_ticket3_vector_index_colab.ipynb
```

Flujo sugerido para el Ticket 1:

```bash
git clone https://github.com/aantoa/bluesea-ai-assistant
cd bluesea-ai-assistant
pip install -r requirements.txt
python -m rag_bsf.cli validate-documents
python -m rag_bsf.cli inventory
```

Si en Colab solo clonas GitHub, es normal que el validador muestre documentos faltantes, porque los documentos fuente no se versionan. Para validar `24/24` en Colab, sube un ZIP privado con las carpetas locales de `documents/`.

El codigo final reutilizable debe quedar en `src/`; los notebooks solo ejecutan y documentan el flujo.

## Arquitectura Prevista

La arquitectura se documenta en detalle en:

```text
docs/architecture.md
```

Arquitectura actual al cierre del Ticket 3:

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

Arquitectura completa prevista para tickets posteriores:

```text
Inventario y documentos locales
  -> validacion documental
  -> extraccion y limpieza
  -> chunks con metadata
  -> embeddings
  -> base vectorial
  -> recuperacion
  -> respuesta del agente con fuentes
  -> deploy en OCI
```

Alcance tecnico actual:

```text
Inventario documental -> validacion de archivos locales -> limpieza Markdown -> chunks con metadata -> embeddings locales -> indice vectorial local
```

## Archivos Clave

| Archivo | Proposito |
| --- | --- |
| `README.md` | Guia principal del proyecto. |
| `requirements.txt` | Instalacion rapida para local, evaluadores y Colab. |
| `pyproject.toml` | Configuracion del paquete Python. |
| `.gitignore` | Protege documentos fuente y salidas locales. |
| `documents/inventory/BSF-INV-001_Document_Inventory.csv` | Inventario maestro de 24 documentos. |
| `docs/architecture.md` | Arquitectura actual y ruta tecnica prevista. |
| `docs/tickets/01_cierre_ticket_documental.md` | Sustento de cierre del Ticket 1. |
| `docs/tickets/02_proceso_extraccion_contenido.md` | Desarrollo tecnico del procesamiento documental. |
| `docs/tickets/02_cierre_ticket_procesamiento.md` | Sustento de cierre del Ticket 2. |
| `docs/tickets/03_indexacion_vectorial.md` | Desarrollo tecnico de la indexacion vectorial local. |
| `docs/tickets/03_cierre_ticket_indexacion.md` | Sustento de cierre del Ticket 3. |
| `notebooks/01_ticket1_inventory_validation_colab.ipynb` | Notebook de apoyo para validar inventario y documentos del Ticket 1 en Colab. |
| `notebooks/02_ticket2_processing_chunks_colab.ipynb` | Notebook de apoyo para pruebas del Ticket 2 en Colab. |
| `notebooks/03_ticket3_vector_index_colab.ipynb` | Notebook de apoyo para pruebas del Ticket 3 en Colab. |
| `src/rag_bsf/` | Codigo del pipeline documental. |
| `scripts/02_process.py` | Ejecucion directa del procesamiento Markdown. |
| `scripts/03_index.py` | Ejecucion directa de la indexacion vectorial local. |
| `data/processed/chunks.jsonl` | Salida local generada por el Ticket 2. |
| `data/index/vectors.jsonl` | Salida local generada por el Ticket 3. |

## Cierre Tecnico Validado

El pipeline debe crecer por tickets. Los archivos compartidos de `src/rag_bsf/` pueden existir desde la base del proyecto, pero cada commit debe mostrar solo la funcionalidad cerrada en esa etapa.

Para el Ticket 1, la parte versionada corresponde a inventario y validacion documental:

```text
src/rag_bsf/config.py
src/rag_bsf/document_loader.py
src/rag_bsf/rag_pipeline.py
src/rag_bsf/schemas.py
src/rag_bsf/cli.py
```

Para el Ticket 2 se agregan o activan:

```text
src/rag_bsf/text_processing.py
scripts/02_process.py
tests/test_text_processing.py
notebooks/02_ticket2_processing_chunks_colab.ipynb
```

Tambien se habilita el comando `process` dentro de `src/rag_bsf/cli.py` y la funcion `process_documents()` dentro de `src/rag_bsf/rag_pipeline.py`.

Para el Ticket 3 se agregan o activan:

```text
src/rag_bsf/embeddings.py
src/rag_bsf/vector_store.py
scripts/03_index.py
tests/test_indexing.py
notebooks/03_ticket3_vector_index_colab.ipynb
docs/tickets/03_indexacion_vectorial.md
docs/tickets/03_cierre_ticket_indexacion.md
```

Tambien se habilita el comando `index` dentro de `src/rag_bsf/cli.py` y la funcion `index_chunks()` dentro de `src/rag_bsf/rag_pipeline.py`.

El inventario maestro no debe modificarse para adaptar el codigo. El ajuste se hace en Python mediante normalizacion de encabezados, para que el pipeline pueda leer columnas como `document_code`, `document_title`, `business_area`, `current_file_name` y `current_relative_path`.

Antes de hacer commit, validar:

```bash
PYTHONPATH=src python -m rag_bsf.cli validate-documents
PYTHONPATH=src python -m rag_bsf.cli inventory
PYTHONPATH=src python -m rag_bsf.cli process
PYTHONPATH=src python -m rag_bsf.cli index
```

Commit sugerido para el Ticket 3:

```bash
git add README.md docs/architecture.md docs/tickets/03_indexacion_vectorial.md docs/tickets/03_cierre_ticket_indexacion.md notebooks/03_ticket3_vector_index_colab.ipynb scripts/03_index.py tests/test_indexing.py src/rag_bsf
git commit -m "Add local vector indexing for Ticket 3"
```

## Siguientes Pasos

1. Probar la indexacion con los documentos Markdown locales completos.
2. Revisar una muestra de vectores y metadata en `data/index/vectors.jsonl`.
3. Iniciar Ticket 4: recuperacion RAG sobre el indice vectorial.
4. Implementar agente de preguntas y respuestas.
5. Documentar ejemplos de preguntas/respuestas.
6. Preparar deploy en OCI.

## Documentation

- [Architecture](docs/architecture.md)
- [Ticket 1 - Recoleccion y organizacion documental](docs/tickets/01_recoleccion_organizacion.md)
- [Ticket 2 - Proceso y extraccion de contenido](docs/tickets/02_proceso_extraccion_contenido.md)
- [Ticket 3 - Indexacion vectorial](docs/tickets/03_indexacion_vectorial.md)
# BlueSea AI Assistant

BlueSea AI Assistant es un agente corporativo de inteligencia artificial diseñado para consultar, interpretar y responder preguntas sobre la documentación interna de BlueSea Foods.

El agente permite centralizar el conocimiento documental de la compañía y responder en lenguaje natural sobre políticas, procedimientos, estándares, documentos legales, financieros, operativos, de calidad, HSE, recursos humanos, tecnología e inventario documental.

A diferencia de un buscador tradicional, el sistema no solo localiza documentos: procesa la pregunta del usuario, recupera evidencia relevante, analiza el contexto disponible y genera una respuesta estructurada con base en fuentes internas. Cuando no existe información suficiente en la base documental, el agente lo indica de forma explícita para evitar respuestas inventadas.

El proyecto combina una interfaz en Streamlit, procesamiento documental, embeddings multilingües, recuperación semántica, control del índice documental y generación de respuestas asistidas por IA.

## Que Incluye

- Interfaz web en Streamlit.
- Procesamiento de documentos internos.
- Indice vectorial local.
- Embeddings multilingues para consultas en espanol e ingles.
- Recuperacion de fuentes documentales.
- Diagnostico del indice usado por la app.

La explicacion tecnica completa esta en:

```text
docs/architecture.md
```

## Estructura Principal

```text
bluesea-ai-assistant/
  app/                  # Aplicacion Streamlit
  documents/            # Documentos fuente por area
  data/                 # Chunks procesados e indice vectorial
  src/rag_bsf/          # Codigo del pipeline RAG
  docs/                 # Documentacion tecnica
  tests/                # Pruebas
  requirements.txt      # Dependencias
  runtime.txt           # Version de Python para Streamlit Cloud
```

## Instalacion Local

Desde la raiz del proyecto:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Preparar el Indice

Antes de usar la app, procesa e indexa los documentos:

```bash
PYTHONPATH=src python -m rag_bsf.cli process
PYTHONPATH=src python -m rag_bsf.cli index
```

Esto genera los archivos necesarios en:

```text
data/processed/
data/index/
```

## Ejecutar la App

```bash
streamlit run app/streamlit_app.py
```

Tambien puedes hacer una pregunta desde consola:

```bash
PYTHONPATH=src python -m rag_bsf.cli ask "What is the expense reimbursement policy?"
```

## Variables de Entorno

Modelo recomendado para embeddings:

```env
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

En Streamlit Cloud, colocarlo en **App settings > Secrets**:

```toml
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

Si usas un modelo de Hugging Face para generacion, tambien puedes configurar:

```toml
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"
HF_MAX_NEW_TOKENS = 450
HF_TEMPERATURE = 0.1
HF_DEBUG = true
```

## Despliegue en Streamlit Cloud

Configuracion recomendada:

| Campo | Valor |
| --- | --- |
| Repository | `aantoa/bluesea-ai-assistant` |
| Branch | `main` |
| Main file path | `app/streamlit_app.py` |
| Python | `3.11` |

El archivo `runtime.txt` debe contener:

```text
python-3.11
```

Para evitar errores del watcher de Streamlit con dependencias opcionales de `transformers`,
el archivo `.streamlit/config.toml` debe contener:

```toml
[server]
fileWatcherType = "none"
```

## Reindexar

Reindexa cuando agregues documentos, cambies el modelo de embeddings: 

```bash
rm -f data/index/vectors.jsonl data/index/embeddings_manifest.json
PYTHONPATH=src python -m rag_bsf.cli process
PYTHONPATH=src python -m rag_bsf.cli index
streamlit cache clear
streamlit run app/streamlit_app.py
```

## Pruebas

```bash
pytest
```

## Notas

- La app principal es `app/streamlit_app.py`.
- La arquitectura detallada esta documentada en `docs/architecture.md`.

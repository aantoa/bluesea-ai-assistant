# Ticket 04 - Camada de recuperacion RAG

## Objetivo

Implementar la capa de recuperacion del RAG a partir del indice vectorial generado en el Ticket 3.

Esta capa decide que fragmentos documentales se entregaran al futuro LLM para generar una respuesta con trazabilidad.

## Entrada

```text
data/index/vectors.jsonl
```

Cada registro contiene:

- chunk original;
- metadata documental;
- vector numerico;
- modelo de embeddings;
- dimensiones del vector.

## Alcance

El Ticket 4 cubre:

- transformacion de la pregunta en embedding;
- busqueda semantica amplia contra el indice local;
- filtros opcionales por metadata;
- reranking local de candidatos;
- seleccion de los mejores fragmentos;
- ensamblaje de contexto con etiquetas de fuente.

El Ticket 4 no cubre:

- generacion de respuestas finales;
- uso de LLM;
- interfaz conversacional;
- base vectorial administrada externa;
- deploy.

## Flujo implementado

```text
pregunta del colaborador
  -> HashingEmbedder
  -> LocalVectorStore.search(candidate_k)
  -> filtros de metadata
  -> reranking local
  -> top_k final
  -> contexto RAG con fuentes
```

## Componentes agregados

| Componente | Archivo | Funcion |
| --- | --- | --- |
| Recuperacion | `src/rag_bsf/retrieval.py` | Recupera candidatos, filtra metadata, rerankea y arma contexto. |
| Pipeline | `src/rag_bsf/rag_pipeline.py` | Expone `retrieve_rag_context()`. |
| CLI | `src/rag_bsf/cli.py` | Agrega comando `retrieve`. |
| Script Ticket 4 | `scripts/04_retrieve.py` | Ejecuta una recuperacion de ejemplo. |
| Notebook Colab | `notebooks/04_ticket4_retrieval_colab.ipynb` | Evidencia recuperacion en Colab. |
| Tests | `tests/test_retrieval.py` | Valida filtros, reranking y contexto. |

## Busqueda semantica

La pregunta se transforma en embedding usando el mismo modelo local de la indexacion:

```text
local-hashing-v1
```

El vector de la pregunta se compara contra los vectores de `vectors.jsonl` usando similitud coseno.

El comando recupera primero un conjunto amplio de candidatos con `candidate_k`, por ejemplo 20.

## Filtros por metadata

La recuperacion permite restringir candidatos con filtros exactos normalizados.

Ejemplo:

```bash
PYTHONPATH=src python -m rag_bsf.cli retrieve "licencia remunerada" --filter category="Human Resources"
```

Los filtros pueden aplicarse sobre campos como:

- `category`;
- `document_code`;
- `title`;
- `status`;
- `confidentiality`.

## Reranking

El reranking local combina:

- score semantico del indice vectorial;
- coincidencia lexical entre pregunta, texto del chunk y metadata relevante.

Esto mejora la precision frente a la busqueda vectorial pura, manteniendo el proyecto reproducible sin APIs externas.

Como el modelo local por hashing no captura sinonimos reales como lo haria un embedding comercial, la recuperacion agrega una expansion controlada de consultas frecuentes. Por ejemplo, `vacaciones` se expande con terminos como `licencia remunerada`, `descanso` y `paid leave`.

## Ensamblaje de contexto

Los chunks finales se convierten en un bloque textual con fuentes:

```text
[S1] BSF-HR-002 | Employee FAQ | section=Paid Leave | category=Human Resources | review_date=N/A
Texto recuperado del chunk...
```

Ese bloque sera la entrada contextual para el prompt del LLM en el siguiente ticket.

## Comandos

Recuperacion basica:

```bash
PYTHONPATH=src python -m rag_bsf.cli retrieve "cuantos dias de vacaciones tengo"
```

Recuperacion con parametros:

```bash
PYTHONPATH=src python -m rag_bsf.cli retrieve "politica de reembolso de gastos" --candidate-k 20 --top-k 5
```

Recuperacion con filtro:

```bash
PYTHONPATH=src python -m rag_bsf.cli retrieve "onboarding obligatorio" --filter category="Human Resources"
```

Script directo:

```bash
PYTHONPATH=src python scripts/04_retrieve.py
```

## Criterio de cierre

El Ticket 4 queda cerrado tecnicamente cuando:

- el indice vectorial puede cargarse sin errores;
- una pregunta se transforma en embedding;
- la busqueda semantica devuelve candidatos;
- los filtros de metadata funcionan;
- el reranking reordena candidatos;
- el contexto final incluye fuentes y metadata;
- las pruebas unitarias de recuperacion pasan correctamente.
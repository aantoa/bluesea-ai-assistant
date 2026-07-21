# Ticket 05 - Produccion y validacion de respuestas

## Objetivo

Implementar la capa que recibe la pregunta del colaborador y el contexto recuperado por el RAG para producir una respuesta basada solo en documentos.

La respuesta debe incluir fuentes verificables y debe evitar inventar informacion cuando los documentos no contienen respaldo suficiente.

## Entrada

```text
RetrievalContext
```

El contexto recuperado incluye:

- pregunta original;
- chunks seleccionados;
- scores de recuperacion y reranking;
- metadata documental;
- bloque de contexto con etiquetas `[S1]`, `[S2]`, etc.

## Alcance

El Ticket 5 cubre:

- construccion de prompt restringido al contexto recuperado;
- generacion local de respuesta basada en frases soportadas;
- citacion con etiquetas de fuente;
- referencias con archivo, seccion, categoria y responsable;
- umbral minimo de confianza;
- fallback cuando no hay contexto suficiente;
- salida estructurada para futura interfaz o integracion con LLM externo.

El Ticket 5 no cubre:

- interfaz web o chat;
- integracion real con un proveedor LLM externo;
- autenticacion de usuarios;
- deploy en OCI;
- base vectorial administrada externa.

## Flujo implementado

```text
pregunta del colaborador
  -> retrieve_rag_context()
  -> RetrievalContext
  -> build_answer_prompt()
  -> validacion de evidencia
  -> respuesta citada o fallback
```

## Componentes agregados

| Componente | Archivo | Funcion |
| --- | --- | --- |
| Generacion de respuesta | `src/rag_bsf/answer_generation.py` | Construye prompt, valida evidencia, selecciona frases soportadas y arma respuesta citada. |
| Esquemas | `src/rag_bsf/schemas.py` | Agrega `AnswerResult` y `AnswerSource`. |
| Pipeline | `src/rag_bsf/rag_pipeline.py` | Expone `answer_question()`. |
| CLI | `src/rag_bsf/cli.py` | Agrega comando `ask`. |
| Script Ticket 5 | `scripts/05_answer.py` | Ejecuta una respuesta de ejemplo. |
| Tests | `tests/test_answer_generation.py` | Valida prompt, citas y fallback. |

## Prompt restringido

El prompt generado incluye instrucciones explicitas:

- responder solo con base en el contexto recuperado;
- no usar conocimiento externo;
- no inventar datos;
- citar cada dato relevante con `[S1]`, `[S2]`, etc.;
- admitir cuando la informacion no esta disponible.

Este contrato permite reemplazar la generacion extractiva local por un LLM externo sin cambiar el resto del pipeline.

## Citacion de fuentes

Cada respuesta fundada conserva trazabilidad hacia los documentos recuperados.

Ejemplo conceptual:

```text
Your entitlement depends on applicable law, employment conditions, and company policy. [S1]

Fuentes: [S1] BSF-HR-002_Employee_FAQ.md, seccion 8.2 How much annual leave do I have?.
```

Cada fuente estructurada contiene:

- etiqueta de fuente;
- codigo documental;
- titulo;
- nombre de archivo;
- seccion;
- categoria;
- responsable;
- score.

## Control de alucinacion

La respuesta solo se genera si:

1. existen resultados recuperados;
2. el mejor score supera el umbral minimo de confianza;
3. se encuentran frases del contexto que puedan sostener la respuesta.

Si alguna condicion falla, el sistema no responde con una conclusion inventada.

## Fallback

Cuando no hay evidencia suficiente, el agente responde:

```text
No encontre esta informacion en los documentos disponibles. Para evitar una respuesta incorrecta, no generare una conclusion sin respaldo documental.
```

Si existe informacion de responsable o categoria, el sistema puede sugerir consultar al area responsable, por ejemplo Recursos Humanos, HSE, Operaciones o Tecnologia.

## Comandos

Respuesta basica:

```bash
PYTHONPATH=src python -m rag_bsf.cli ask "cuantos dias de vacaciones tengo"
```

Respuesta con filtro:

```bash
PYTHONPATH=src python -m rag_bsf.cli ask "cuantos dias de vacaciones tengo" --filter category="Human Resources"
```

Respuesta con umbral de confianza:

```bash
PYTHONPATH=src python -m rag_bsf.cli ask "politica de beneficios" --min-confidence 0.25
```

Script directo:

```bash
PYTHONPATH=src python scripts/05_answer.py
```

## Criterio de cierre

El Ticket 5 queda cerrado tecnicamente cuando:

- el comando `ask` genera una respuesta con fuentes;
- el prompt contiene instrucciones anti-alucinacion;
- las referencias incluyen archivo y seccion;
- el fallback se activa sin contexto;
- el fallback se activa por baja confianza;
- las pruebas unitarias de generacion de respuesta pasan correctamente.
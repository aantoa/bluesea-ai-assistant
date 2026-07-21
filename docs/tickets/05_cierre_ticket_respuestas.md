# Cierre Ticket 05 - Produccion y validacion de respuestas

## Resumen

El Ticket 5 incorpora la capa de respuesta del asistente RAG de BlueSea Foods.

La implementacion toma la pregunta del colaborador, recupera contexto documental con la capa del Ticket 4, construye un prompt restringido y genera una respuesta basada solo en evidencia recuperada. Si no hay contexto suficiente, el sistema responde con fallback en lugar de inventar informacion.

## Entrada

```text
data/index/vectors.jsonl
RetrievalContext
```

La recuperacion previa entrega chunks, scores y metadata documental.

## Proceso cerrado

1. Recibir la pregunta del colaborador.
2. Recuperar contexto con `retrieve_rag_context()`.
3. Construir un prompt con pregunta, instrucciones y contexto.
4. Validar si hay resultados recuperados.
5. Evaluar el mejor score contra el umbral minimo de confianza.
6. Seleccionar frases soportadas por el contexto.
7. Generar respuesta con citas `[S1]`, `[S2]`, etc.
8. Adjuntar fuentes estructuradas.
9. Aplicar fallback cuando no hay evidencia suficiente.

## Salida

La salida principal es un `AnswerResult` con:

```text
question
answer
sources
prompt
grounded
fallback_reason
```

Ejemplo de respuesta fundada:

```text
Your entitlement depends on applicable law, employment conditions, and company policy. [S1]

Fuentes: [S1] BSF-HR-002_Employee_FAQ.md, seccion 8.2 How much annual leave do I have?.
```

Ejemplo de fallback:

```text
No encontre esta informacion en los documentos disponibles. Para evitar una respuesta incorrecta, no generare una conclusion sin respaldo documental.
```

## Archivos implementados o modificados

```text
src/rag_bsf/answer_generation.py
src/rag_bsf/schemas.py
src/rag_bsf/rag_pipeline.py
src/rag_bsf/cli.py
scripts/05_answer.py
notebooks/05_ticket5_answer_generation_colab.ipynb
tests/test_answer_generation.py
docs/tickets/05_generacion_respuestas.md
docs/tickets/05_cierre_ticket_respuestas.md
README.md
docs/architecture.md
```

## Comandos de validacion

Respuesta con citas:

```bash
PYTHONPATH=src python -m rag_bsf.cli ask "cuantos dias de vacaciones tengo" --filter category="Human Resources"
```

Validacion de codigo:

```bash
python -m compileall src tests scripts
```

Pruebas unitarias esperadas:

```bash
PYTHONPATH=src pytest tests/test_answer_generation.py
```

En el entorno actual, `pytest` puede no estar instalado. En ese caso, se valida con `compileall` y ejecucion directa de las funciones de prueba.

Evidencia en notebook:

```text
notebooks/05_ticket5_answer_generation_colab.ipynb
```

## Controles anti-alucinacion

El sistema no genera respuesta fundada cuando:

- no existen chunks recuperados;
- el score de recuperacion es menor al umbral configurado;
- no se detectan frases soportadas por el contexto.

En esos casos, `grounded=False` y `fallback_reason` indica la causa tecnica.

## Contactos o responsables

La metadata documental contiene `owner` y `category`. Cuando existe un responsable en el chunk recuperado, el fallback puede sugerir consultar a ese responsable.

Si no hay owner recuperado, se usa una tabla local de areas responsables por categoria. Esto cubre la nota del ticket sobre revisar si los contactos de las areas existen dentro del banco conocido por el agente.

## Alcance no incluido

El Ticket 5 no implementa todavia:

- interfaz conversacional;
- autenticacion;
- integracion real con proveedor LLM externo;
- mensajeria por Teams o Slack;
- despliegue en OCI.

## Estado final

Ticket 05 cerrado tecnicamente. La respuesta final queda conectada al contexto recuperado, con prompt restringido, citas de fuente, validacion de confianza y fallback explicito cuando no hay respaldo documental.

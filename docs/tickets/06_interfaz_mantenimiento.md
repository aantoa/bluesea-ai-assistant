# Ticket 6 - Implantacion, interfaz y mantenimiento

## Objetivo

Implementar una interfaz simple, funcional y mantenible para que el agente RAG de BlueSea Foods pueda ser usado por colaboradores sin ejecutar comandos tecnicos.

El alcance del ticket no busca construir una plataforma corporativa productiva completa, sino demostrar que el agente puede:

- recibir preguntas en lenguaje natural;
- consultar documentos corporativos indexados;
- generar respuestas basadas en evidencia;
- mostrar fuentes consultadas;
- conservar historial durante la sesion;
- registrar trazabilidad basica de uso;
- permitir mantenimiento minimo del indice documental.

## Canal elegido

Se eligio un chat web dedicado construido con Streamlit.

Esta opcion es adecuada para el proyecto porque:

- permite una implementacion rapida;
- no requiere infraestructura adicional para la validacion academica;
- puede ejecutarse localmente;
- se conecta directamente con el pipeline Python existente;
- facilita integrar chat, fuentes, logs, diagnostico y reindexacion en una sola pantalla.

Slack, Teams u otros canales corporativos quedan como alternativas futuras. No se implementan en este ticket porque requieren configuracion externa, autenticacion, permisos corporativos y administracion de usuarios.

## Integracion con tickets anteriores

La interfaz consume las funciones del pipeline ya construido en los tickets previos:

| Ticket previo | Componente reutilizado | Uso dentro de la interfaz |
| --- | --- | --- |
| Ticket 1 | Inventario documental | Identificacion de documentos disponibles. |
| Ticket 2 | Procesamiento y chunking | Preparacion de contenido indexable. |
| Ticket 3 | Indice vectorial local | Consulta del indice `data/index/vectors.jsonl`. |
| Ticket 4 | Recuperacion documental | Busqueda de evidencia relevante. |
| Ticket 5 | Generacion de respuesta | Funcion `answer_question()` para responder con fuentes o fallback. |

La aplicacion evita duplicar logica de recuperacion, generacion, citacion o fallback. Su rol es actuar como capa de uso, visualizacion y mantenimiento.

## Estructura implementada

```text
app/
  streamlit_app.py
  style.css
  assets/

src/
  rag_bsf/
    answer_generation.py
    cli.py
    config.py
    document_loader.py
    embeddings.py
    rag_pipeline.py
    retrieval.py
    schemas.py
    text_processing.py
    vector_store.py

logs/
  execution_logs.jsonl
  execution_logs.csv
```

## Funcionalidades implementadas

| Requisito | Implementacion |
| --- | --- |
| Identificar que es un agente de IA | Encabezado corporativo: `BSF Assistant - Agente IA Documental`. |
| Campo de pregunta | Formulario central con `st.text_area()` y boton `Enviar consulta`. |
| Consulta documental | Ejecucion de `answer_question(question, top_k=5, candidate_k=30)`. |
| Historial de conversacion | Mensajes guardados en `st.session_state["history"]` y mostrados en panel con scroll. |
| Respuesta con fuentes | La respuesta incluye bloque de respuesta directa y fuentes consultadas. |
| Trazabilidad lateral | Panel derecho con area detectada, estado de respuesta, fuentes usadas y ultimas ejecuciones. |
| Inventario documental | Panel izquierdo con archivos soportados, documentos indexables, formatos y areas detectadas. |
| Reindexacion manual | Boton `Reindexar documentos` que ejecuta procesamiento e indexacion desde la interfaz. |
| Logs de ejecucion | Registro JSONL con pregunta, respuesta, area, fuentes, tiempo y estado. |
| Exportacion de logs | Generacion y descarga de `execution_logs.csv`. |
| Diagnostico de documentos | Expander con carpeta leida, archivos encontrados, soportados y omitidos. |
| Manejo de documentos vacios | Advertencia si no hay documentos soportados en `documents/`. |
| Diseno corporativo | CSS propio con colores BSF, paneles, footer, tarjetas, tags y scroll controlado. |
| Correccion de HTML duro | Render de chat sin f-string multilinea indentado y limpieza de HTML antiguo en historial. |
| Iconografia de chat | Icono SVG de usuario para preguntas y robot para respuestas del asistente. |

## Detalles tecnicos de la interfaz

### Carga inicial

La aplicacion configura la pagina, carga estilos CSS, inicializa variables de sesion, obtiene el inventario documental y renderiza tres paneles:

- panel izquierdo: estado del agente y mantenimiento documental;
- panel central: conversacion con el agente;
- panel derecho: trazabilidad, fuentes y logs recientes.

### Historial de conversacion

El historial se conserva durante la sesion en:

```python
st.session_state["history"]
```

Cada consulta agrega dos mensajes:

```python
{"role": "user", "content": clean_message_text(question)}
{"role": "assistant", "content": clean_message_text(answer)}
```

Para evitar que Streamlit muestre HTML como texto plano, el render del chat se construye con cadenas HTML compactas, sin indentacion multilinea que pueda ser interpretada por Markdown como bloque de codigo.

### Limpieza de HTML antiguo

Se incluyo una funcion de limpieza para mensajes guardados previamente con HTML accidental:

```python
clean_message_text()
```

Esta funcion:

- decodifica entidades HTML escapadas;
- elimina tarjetas HTML antiguas;
- convierte saltos y listas a texto legible;
- elimina etiquetas remanentes;
- evita que aparezcan bloques como `<article>`, `<div>` o `&lt;article`.

### Render del chat

El historial se renderiza mediante:

```python
render_message_history()
chat_history_html()
render_basic_markdown()
```

La estructura final muestra tarjetas diferenciadas para usuario y asistente, con iconos SVG y scroll interno.

### Registro de logs

Cada consulta registra un evento en:

```text
logs/execution_logs.jsonl
```

El registro contiene:

- fecha y hora;
- pregunta;
- respuesta generada;
- area detectada;
- fuentes consultadas;
- tiempo de respuesta;
- estado de respuesta.

Tambien se genera un CSV descargable desde la interfaz:

```text
logs/execution_logs.csv
```

### Reindexacion desde la interfaz

El panel izquierdo incluye el boton:

```text
Reindexar documentos
```

Este boton ejecuta:

```python
process_documents(root_dir=DOCS_DIR)
index_chunks()
```

Con ello se actualizan los documentos procesados y el indice vectorial local sin tener que usar comandos manuales.

## Ejecucion local

Desde la carpeta del proyecto mejorado:

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Antes de usar la interfaz por primera vez, se recomienda generar los artefactos del pipeline:

```bash
PYTHONPATH=src python -m rag_bsf.cli process
PYTHONPATH=src python -m rag_bsf.cli index
```

El agente usa el indice vectorial local:

```text
data/index/vectors.jsonl
```

## Flujo de uso

1. El colaborador abre la interfaz Streamlit.
2. Revisa el estado del agente en el panel izquierdo.
3. Escribe una pregunta sobre politicas, procesos o documentos corporativos.
4. La aplicacion ejecuta `answer_question()`.
5. El agente responde con evidencia documental o activa fallback si no hay sustento suficiente.
6. La respuesta y la pregunta quedan visibles en el historial de la sesion.
7. El panel derecho muestra area detectada, fuentes y ultimas ejecuciones.
8. La consulta queda registrada en logs.
9. Si se actualizan documentos, el usuario puede reindexar desde la interfaz.

## Mantenimiento continuo

### Actualizacion de documentos

Cuando se agregue, modifique o elimine un documento en `documents/`, se debe reprocesar e indexar:

```bash
PYTHONPATH=src python -m rag_bsf.cli process
PYTHONPATH=src python -m rag_bsf.cli index
```

Tambien puede utilizarse el boton `Reindexar documentos` desde la interfaz.

### Curaduria de contenido

Cada area responsable debe revisar periodicamente sus documentos:

- Human Resources;
- Quality and Certifications;
- HSE;
- Operations;
- Technology;
- Corporate;
- Document Control.

El objetivo es evitar que el agente responda con documentos desactualizados, ambiguos o incompletos.

### Monitoreo de calidad

La interfaz registra informacion operativa suficiente para una primera supervision:

- pregunta;
- respuesta;
- fuentes;
- area documental detectada;
- fecha y hora;
- tiempo de respuesta;
- estado de respuesta;
- razon de fallback si aplica.

Estas metricas permiten identificar preguntas sin respuesta, documentos faltantes, temas recurrentes y posibles ajustes al umbral de confianza.

### Ciclo de mejora

Las preguntas recurrentes sin buena respuesta deben revisarse para decidir si:

- falta agregar un documento;
- el documento existe pero esta mal estructurado;
- se debe mejorar la redaccion del documento fuente;
- se debe ajustar el umbral de recuperacion;
- se debe mejorar el prompt;
- se debe mejorar la recuperacion o el reranking.

### Actualizacion del modelo

La implementacion actual prioriza reproducibilidad local. En una version productiva se puede conectar un LLM externo manteniendo el mismo contrato:

```text
pregunta + contexto recuperado -> respuesta citada o fallback
```

Antes de cambiar el modelo en produccion, se deben comparar:

- calidad de respuesta;
- precision de citas;
- frecuencia de fallback;
- tiempo de respuesta;
- costo operativo;
- trazabilidad de fuentes.

## Validacion realizada

Se valido que el codigo Python compile correctamente:

```bash
python -m py_compile app/streamlit_app.py src/rag_bsf/*.py
```

La validacion confirma que la interfaz y los modulos del pipeline no presentan errores de sintaxis.

## Alcance no incluido

Este ticket no incluye:

- autenticacion de usuarios;
- roles y permisos;
- persistencia de feedback por usuario;
- integracion con Slack o Teams;
- despliegue cloud;
- monitoreo productivo automatizado;
- administracion de versiones documentales desde la interfaz;
- aprobaciones corporativas para publicacion.

Estos puntos quedan como evolucion natural para tickets posteriores.

## Resultado

El Ticket 6 queda actualizado como una interfaz funcional para uso y mantenimiento basico del agente documental BSF. La aplicacion permite consultar el agente, revisar fuentes, conservar historial, registrar ejecuciones, descargar logs y reindexar documentos desde una pantalla web local.

from __future__ import annotations

import csv
import base64
import html
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import streamlit as st


APP_TITLE = "BSF Corporate AI Agent"
APP_SUBTITLE = "Agente corporativo para consultas documentales internas"

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
DOCS_DIR = PROJECT_ROOT / "documents"
LOGS_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOGS_DIR / "execution_logs.jsonl"
CSS_FILE = BASE_DIR / "style.css"
ASSETS_DIR = BASE_DIR / "assets"
LOGO_CANDIDATES = [
    ASSETS_DIR / "bluesea_ai_icon.png",
    ASSETS_DIR / "bsf_logo_full_color.png",
    ASSETS_DIR / "logo.png",
    ASSETS_DIR / "logo_bsf.png",
]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rag_bsf.config import SUPPORTED_SOURCE_EXTENSIONS  # noqa: E402
from rag_bsf.document_loader import discover_source_documents  # noqa: E402
from rag_bsf.rag_pipeline import answer_question, index_chunks, process_documents  # noqa: E402
from rag_bsf.schemas import AnswerResult  # noqa: E402


def configure_page() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="BSF",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def load_css() -> None:
    if CSS_FILE.exists():
        st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def compact_html(raw: str) -> str:
    """Colapsa espacios/saltos de línea entre etiquetas.

    Streamlit renderiza el HTML de st.markdown(unsafe_allow_html=True) pasando
    primero por el parser de Markdown. Si el HTML queda con indentación real
    (saltos de línea + 4+ espacios), Markdown lo interpreta como un bloque de
    código y lo muestra como texto plano en vez de renderizarlo. Esta función
    aplana el HTML a una sola línea lógica para evitar ese problema.
    """
    text = raw.strip()
    text = re.sub(r">\s+<", "><", text)
    return text


def initialize_state() -> None:
    defaults = {
        "history": [],
        "last_question": "",
        "last_sources": [],
        "last_area": "General",
        "last_grounded": False,
        "last_stats": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    st.session_state["history"] = [
        {**item, "content": clean_message_text(item.get("content", ""))}
        for item in st.session_state["history"]
    ]

def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    mime = "image/svg+xml" if path.suffix.lower() == ".svg" else "image/png"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def find_logo_file() -> Path | None:
    for path in LOGO_CANDIDATES:
        if path.exists():
            return path
    if ASSETS_DIR.exists():
        for path in sorted(ASSETS_DIR.iterdir()):
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".webp"}:
                return path
    return None


def clean_message_text(content: str) -> str:
    text = str(content or "")

    # Streamlit puede conservar HTML viejo escapado en session_state.
    previous = None
    for _ in range(6):
        if text == previous:
            break
        previous = text
        text = html.unescape(text)

    if "message-body" in text:
        body_match = re.search(
            r'<div[^>]*class=["\'][^"\']*message-body[^"\']*["\'][^>]*>(.*?)</div>',
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if body_match:
            text = body_match.group(1)

    text = re.sub(r"```(?:html|HTML)?\s*", "", text)
    text = text.replace("```", "")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li[^>]*>", "- ", text, flags=re.IGNORECASE)
    text = re.sub(r"</(?:p|li|div|article|section|ul|ol|h[1-6])>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(?:strong|b)>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?(?:strong|span|em|b|i)[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&(?:lt|gt|amp|quot|#x27|nbsp);", " ", text)
    text = re.sub(r"^\s*IA\s*", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()

def render_basic_markdown(content: str) -> str:
    text = clean_message_text(content)
    escaped = html.escape(text)

    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r'<span class="inline-code">\1</span>', escaped)

    lines = escaped.splitlines()
    rendered_lines: list[str] = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_list:
                rendered_lines.append("</ul>")
                in_list = False
            continue

        if stripped.startswith("- "):
            if not in_list:
                rendered_lines.append("<ul>")
                in_list = True
            rendered_lines.append(f"<li>{stripped[2:]}</li>")
        else:
            if in_list:
                rendered_lines.append("</ul>")
                in_list = False
            rendered_lines.append(f"<p>{stripped}</p>")

    if in_list:
        rendered_lines.append("</ul>")

    return "".join(rendered_lines)

def user_icon_svg() -> str:
    return """
    <svg class="chat-svg-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M20 21a8 8 0 0 0-16 0" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
    </svg>
    """


def robot_icon_svg() -> str:
    return """
    <svg class="chat-svg-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="5" y="7" width="14" height="12" rx="3" stroke="currentColor" stroke-width="2"/>
        <path d="M12 3v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <circle cx="9" cy="13" r="1" fill="currentColor"/>
        <circle cx="15" cy="13" r="1" fill="currentColor"/>
        <path d="M9 17h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>
    """


def chat_history_html(messages: list[dict]) -> str:
    if not messages:
        return (
            '<div class="chat-frame empty-chat">'
            '<div>'
            '<strong>Haz una consulta documental</strong>'
            '<p>El historial aparecerá aquí y tendrá scroll propio cuando crezca.</p>'
            '</div>'
            '</div>'
        )

    cards: list[str] = []

    for item in messages:
        role = item.get("role", "assistant")
        role_class = "user" if role == "user" else "assistant"
        role_label = "Consulta del colaborador" if role == "user" else "Respuesta directa"
        icon_html = user_icon_svg() if role == "user" else robot_icon_svg()
        content = render_basic_markdown(item.get("content", ""))

        cards.append(
            f'<article class="message-card {html.escape(role_class)}">'
            f'<div class="message-icon">{icon_html}</div>'
            f'<div class="message-body">'
            f'<strong>{html.escape(role_label)}</strong>'
            f'{content}'
            f'</div>'
            f'</article>'
        )

    return f'<div class="chat-frame">{"".join(cards)}</div>'

@st.cache_data(show_spinner=False)
def get_document_inventory() -> dict:
    supported_extensions = set(SUPPORTED_SOURCE_EXTENSIONS)
    all_files = [path for path in sorted(DOCS_DIR.rglob("*")) if path.is_file()] if DOCS_DIR.exists() else []
    supported_files = [
        path for path in all_files
        if path.suffix.lower() in supported_extensions and not path.name.startswith(".")
    ]
    unsupported_files = [
        path for path in all_files
        if path.suffix.lower() not in supported_extensions and not path.name.startswith(".")
    ]
    records = discover_source_documents(root_dir=DOCS_DIR)

    return {
        "total_files": len(all_files),
        "supported_files": len(supported_files),
        "unsupported_files": [str(path.relative_to(PROJECT_ROOT)) for path in unsupported_files],
        "records": records,
        "areas": sorted({record.category for record in records if record.category}),
        "extensions": sorted({path.suffix.lower().lstrip(".") for path in supported_files}),
    }


def reindex_documents() -> dict:
    get_document_inventory.clear()
    stats = process_documents(root_dir=DOCS_DIR)
    index_stats = index_chunks()
    combined = {**stats, **{f"index_{key}": value for key, value in index_stats.items()}}
    st.session_state["last_stats"] = combined
    get_document_inventory.clear()
    return combined


def write_execution_log(payload: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_recent_logs(limit: int = 5) -> list[dict]:
    if not LOG_FILE.exists():
        return []

    logs: list[dict] = []
    for line in LOG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]:
        try:
            logs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return logs[::-1]


def export_logs_csv() -> str:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logs = read_recent_logs(limit=5000)
    if not logs:
        return ""

    csv_path = LOGS_DIR / "execution_logs.csv"
    fieldnames = [
        "timestamp",
        "question",
        "detected_area",
        "sources",
        "response_time_seconds",
        "status",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in logs:
            writer.writerow(
                {
                    "timestamp": item.get("timestamp", ""),
                    "question": item.get("question", ""),
                    "detected_area": item.get("detected_area", ""),
                    "sources": ", ".join(item.get("sources", [])),
                    "response_time_seconds": item.get("response_time_seconds", ""),
                    "status": item.get("status", ""),
                }
            )
    return str(csv_path)


def source_names(result: AnswerResult) -> list[str]:
    return [
        f"{source.document_code} - {source.filename}"
        for source in result.sources
    ]


def detected_area(result: AnswerResult) -> str:
    if result.sources:
        return result.sources[0].category or "General"
    return "General"


def render_header() -> None:
    logo_file = find_logo_file()
    logo_uri = image_data_uri(logo_file) if logo_file else ""
    logo_html = (
        f'<img class="brand-logo" src="{logo_uri}" alt="BSF logo">'
        if logo_uri
        else '<div class="brand-mark"><span></span><span></span></div>'
    )
    st.markdown(
        compact_html(
            f"""
            <header class="topbar">
                <div class="brand-block">
                    {logo_html}
                    <div class="brand-copy">
                        <strong>BSF</strong>
                        <span>Assistant</span>
                    </div>
                    <div class="brand-divider"></div>
                    <div class="product-name">Agente IA Documental</div>
                </div>
                <div class="user-block">
                    <span class="secure-pill">Entorno Corporativo</span>
                    <span class="avatar">MP</span>
                    <div>
                        <strong>Amalia Anto</strong>
                        <small>Analista Senior</small>
                    </div>
                </div>
            </header>
            """
        ),
        unsafe_allow_html=True,
    )


def render_message_history() -> None:
    messages = st.session_state["history"][-12:]
    st.markdown(
        compact_html(f'<section class="chat-scroll">{chat_history_html(messages)}</section>'),
        unsafe_allow_html=True,
    )

def render_left_panel(inventory: dict) -> None:
    st.markdown('<div class="panel-title">Centro del agente</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-heading">Estado del agente</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-pill online">Activo</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    col_a.metric("Archivos soportados", inventory["supported_files"])
    col_b.metric("Docs indexables", len(inventory["records"]))
    st.metric("Archivos en documents", inventory["total_files"])

    if st.button("Reindexar documentos", use_container_width=True):
        with st.spinner("Procesando documentos y reconstruyendo índice..."):
            stats = reindex_documents()
        st.success(f"Índice actualizado: {stats.get('documents', 0)} documentos, {stats.get('chunks', 0)} chunks.")

    if st.session_state["last_stats"]:
        stats = st.session_state["last_stats"]
        st.caption(
            f"Último índice: {stats.get('documents', 0)} documentos, "
            f"{stats.get('chunks', 0)} chunks, {stats.get('index_vectors', 0)} vectores."
        )

    st.markdown('<div class="panel-heading">Formatos detectados</div>', unsafe_allow_html=True)
    extensions = inventory["extensions"] or [ext.lstrip(".") for ext in SUPPORTED_SOURCE_EXTENSIONS]
    st.markdown(
        "".join(f'<span class="tag">{html.escape(extension.upper())}</span>' for extension in extensions),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel-heading">Áreas corporativas</div>', unsafe_allow_html=True)
    for area in inventory["areas"] or ["General"]:
        st.markdown(f'<div class="area-item">{html.escape(area)}</div>', unsafe_allow_html=True)

    with st.expander("Diagnóstico de documentos"):
        st.write(f"Carpeta leída: `{DOCS_DIR}`")
        st.write(f"Archivos encontrados: `{inventory['total_files']}`")
        st.write(f"Archivos soportados: `{inventory['supported_files']}`")
        st.write(f"Registros indexables: `{len(inventory['records'])}`")
        if inventory["unsupported_files"]:
            st.write("Archivos omitidos por extensión:")
            for item in inventory["unsupported_files"][:30]:
                st.code(item, language=None)


def render_chat_panel() -> None:
    st.markdown(
        compact_html(
            """
            <div class="panel-title-row">
                <div>
                    <div class="panel-title">Consulta del colaborador</div>
                    <p>El agente utiliza IA y evidencia documental para responder con trazabilidad.</p>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    render_message_history()

    with st.form("question_form", clear_on_submit=True):
        question = st.text_area(
            "Pregunta",
            placeholder="Escribe una pregunta sobre políticas, procesos, calidad, legal, RH...",
            label_visibility="collapsed",
            height=72,
        )
        submitted = st.form_submit_button("Enviar consulta", use_container_width=True)
    if not submitted:
        return
    question = question.strip()
    if not question:
        return

    start_time = time.perf_counter()
    with st.spinner("Buscando evidencia documental..."):
        result = answer_question(question, top_k=5, candidate_k=30)
    elapsed = round(time.perf_counter() - start_time, 3)

    sources = source_names(result)
    area = detected_area(result)
    status = "grounded" if result.grounded else f"no_evidence:{result.fallback_reason or 'unknown'}"

    answer = (
        f"**Respuesta**\n\n{result.answer}\n\n"
        f"**Fuentes consultadas**\n\n"
        + ("\n".join(f"- `{source}`" for source in sources) if sources else "- No se recuperaron fuentes suficientes.")
    )

    st.session_state["history"].append({"role": "user", "content": clean_message_text(question)})
    st.session_state["history"].append({"role": "assistant", "content": clean_message_text(answer)})
    st.session_state["last_question"] = question
    st.session_state["last_sources"] = sources
    st.session_state["last_area"] = area
    st.session_state["last_grounded"] = result.grounded

    write_execution_log(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "question": question,
            "answer": result.answer,
            "detected_area": area,
            "sources": sources,
            "response_time_seconds": elapsed,
            "status": status,
        }
    )
    st.rerun()


def render_right_panel() -> None:
    st.markdown('<div class="panel-title">Trazabilidad</div>', unsafe_allow_html=True)
    grounded_label = "Con evidencia" if st.session_state["last_grounded"] else "Pendiente / sin evidencia"
    st.markdown(
        compact_html(
            f"""
            <div class="trace-card">
                <span>Área detectada</span>
                <strong>{html.escape(st.session_state["last_area"])}</strong>
            </div>
            <div class="trace-card">
                <span>Estado de respuesta</span>
                <strong>{html.escape(grounded_label)}</strong>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel-heading">Fuentes usadas</div>', unsafe_allow_html=True)
    if st.session_state["last_sources"]:
        for source in st.session_state["last_sources"]:
            st.markdown(f'<div class="source-item">{html.escape(source)}</div>', unsafe_allow_html=True)
    else:
        st.info("Aún no hay fuentes consultadas en esta sesión.")

    st.markdown('<div class="panel-heading">Últimas ejecuciones</div>', unsafe_allow_html=True)
    logs = read_recent_logs()
    if logs:
        for log in logs:
            st.markdown(
                compact_html(
                    f"""
                    <div class="log-item">
                        <strong>{html.escape(log.get("detected_area", "General"))}</strong>
                        <span>{html.escape(log.get("timestamp", ""))}</span>
                        <p>{html.escape(log.get("question", "")[:120])}</p>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )
    else:
        st.caption("Los logs aparecerán después de la primera consulta.")

    csv_path = export_logs_csv()
    if csv_path:
        with open(csv_path, "rb") as file:
            st.download_button(
                "Descargar logs CSV",
                data=file,
                file_name="execution_logs.csv",
                mime="text/csv",
                use_container_width=True,
            )


def render_empty_documents_warning(inventory: dict) -> None:
    if inventory["supported_files"]:
        return
    st.warning(
        f"No se encontraron documentos soportados en `{DOCS_DIR}`. "
        "Agrega archivos `.md`, `.txt`, `.csv`, `.json`, `.html`, `.pdf`, `.docx`, `.pptx` o `.xlsx`."
    )


def main() -> None:
    configure_page()
    load_css()
    initialize_state()

    inventory = get_document_inventory()
    render_header()
    render_empty_documents_warning(inventory)

    left, center, right = st.columns([1.05, 2.1, 1.15], gap="small")
    with left:
        with st.container(border=True):
            render_left_panel(inventory)
    with center:
        with st.container(border=True):
            render_chat_panel()
    with right:
        with st.container(border=True):
            render_right_panel()

    st.markdown(
        compact_html(
            """
            <footer class="app-footer">
                BSF Corporate AI Agent | Evidence-based answers | Execution logging enabled
            </footer>
            """
        ),
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
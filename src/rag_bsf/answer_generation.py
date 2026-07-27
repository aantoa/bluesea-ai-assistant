from __future__ import annotations

import re

from rag_bsf.embeddings import TOKEN_RE
from rag_bsf.retrieval import expand_query
from rag_bsf.schemas import AnswerResult, AnswerSource, RetrievalContext, SearchResult


DEFAULT_MIN_CONFIDENCE = 0.18
DEFAULT_MAX_SENTENCES = 4
METADATA_LINE_RE = re.compile(
    r"^\s*(document\s+code|document\s+title|keywords?|document\s+type|business\s+area|"
    r"owner|functional\s+approver|applicable\s+sites|source|format|version|approval|"
    r"review\s+date|current_file_name|file_name|folder|category)\s*(?:[:|-]|\s+)",
    flags=re.IGNORECASE,
)
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
CONTROLLED_SECTION_RE = re.compile(
    r"^\s*(document information|revision history|approval|approvals?|keywords?|metadata)\s*$",
    flags=re.IGNORECASE,
)
DEFAULT_AREA_CONTACTS = {
    "Corporate": "Corporate Affairs Manager",
    "Corporate Knowledge Management": "Knowledge Management Lead",
    "Document Control": "Document Control Lead",
    "Finance": "Finance Manager",
    "Human Resources": "Human Resources Manager",
    "HSE": "HSE Manager",
    "IT": "IT Service Desk Lead",
    "Legal / Compliance": "Compliance Officer",
    "Legal and Compliance": "Compliance Officer",
    "Operations": "Operations Manager",
    "Quality and Certifications": "Quality Manager",
    "Technology": "IT Service Desk Lead",
}


def generate_grounded_answer(
    question: str,
    retrieved: RetrievalContext,
    *,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    max_sentences: int = DEFAULT_MAX_SENTENCES,
    area_contacts: dict[str, str] | None = None,
) -> AnswerResult:
    """Generate a cited answer using only retrieved context."""

    prompt = build_answer_prompt(question, retrieved.context)
    contacts = {**DEFAULT_AREA_CONTACTS, **(area_contacts or {})}
    fallback_reason = fallback_reason_for(retrieved, min_confidence)

    if fallback_reason:
        return AnswerResult(
            question=question,
            answer=build_fallback_answer(question, retrieved, contacts),
            sources=[],
            prompt=prompt,
            grounded=False,
            fallback_reason=fallback_reason,
        )

    selected_sentences = select_supported_sentences(
        question,
        retrieved.results,
        max_sentences=max_sentences,
    )
    if not selected_sentences:
        return AnswerResult(
            question=question,
            answer=build_fallback_answer(question, retrieved, contacts),
            sources=[],
            prompt=prompt,
            grounded=False,
            fallback_reason="no_supported_sentences",
        )

    answer = format_answer(selected_sentences)
    used_labels = source_labels_in(selected_sentences)
    sources = build_answer_sources(retrieved.results, allowed_labels=used_labels)
    references = "; ".join(
        f"[{source.source_label}] {source.filename}, seccion {source.section}"
        for source in sources
    )
    answer = f"{answer}\n\nFuentes: {references}."

    return AnswerResult(
        question=question,
        answer=answer,
        sources=sources,
        prompt=prompt,
        grounded=True,
    )


def build_answer_prompt(question: str, context: str) -> str:
    return (
        "Eres el asistente interno de BlueSea Foods.\n"
        "Responde unicamente con base en el CONTEXTO RECUPERADO.\n"
        "No uses conocimiento externo ni inventes datos.\n"
        "Cita cada dato relevante con la etiqueta de fuente [S1], [S2], etc.\n"
        "Si el contexto no contiene la informacion necesaria, responde claramente: "
        "\"No encontre esta informacion en los documentos disponibles\".\n\n"
        f"PREGUNTA:\n{question.strip()}\n\n"
        f"CONTEXTO RECUPERADO:\n{context.strip() if context.strip() else '(sin contexto recuperado)'}\n\n"
        "RESPUESTA:"
    )


def fallback_reason_for(retrieved: RetrievalContext, min_confidence: float) -> str:
    if not retrieved.results:
        return "no_retrieved_context"

    best_score = max(result.score for result in retrieved.results)
    if best_score < min_confidence:
        return "low_retrieval_confidence"

    return ""


def build_fallback_answer(
    question: str,
    retrieved: RetrievalContext,
    area_contacts: dict[str, str],
) -> str:
    area = infer_area(retrieved)
    owner = infer_owner(retrieved, area_contacts, area)
    owner_suffix = f" Puedes consultar al area responsable: {owner}." if owner else ""
    return (
        "No encontre esta informacion en los documentos disponibles. "
        "Para evitar una respuesta incorrecta, no generare una conclusion sin respaldo documental."
        f"{owner_suffix}"
    )


def select_supported_sentences(
    question: str,
    results: list[SearchResult],
    *,
    max_sentences: int,
) -> list[str]:
    query_terms = token_set(expand_query(question))
    ranked_by_result: list[list[tuple[float, str]]] = []

    for result in results:
        result_sentences: list[tuple[float, str]] = []
        candidates = extract_answer_candidates(result.chunk.text)
        for sentence in candidates:
            if sentence.endswith("?") or sentence[:1].islower() or is_noise_sentence(sentence):
                continue
            sentence_terms = token_set(sentence)
            if not sentence_terms:
                continue
            overlap = len(query_terms & sentence_terms) / max(1, len(query_terms))
            if overlap <= 0 and not has_intent_phrase(query_terms, sentence):
                continue
            score = result.score + overlap + candidate_quality_bonus(sentence)
            result_sentences.append((score, ensure_source_citation(sentence, result.source_label)))
        result_sentences.sort(key=lambda item: item[0], reverse=True)
        ranked_by_result.append(result_sentences)

    if ranked_by_result and ranked_by_result[0]:
        return dedupe_sentences(ranked_by_result[0], max_sentences=max_sentences)

    ranked = [sentence for group in ranked_by_result for sentence in group]
    ranked.sort(key=lambda item: item[0], reverse=True)
    return dedupe_sentences(ranked, max_sentences=max_sentences)


def extract_answer_candidates(text: str) -> list[str]:
    """Extract readable answer snippets from retrieved chunks.

    Source chunks often contain front matter, table rows, document headers and keyword
    strings. Those are useful for retrieval but poor as final answers, so this
    function turns the chunk into human-readable candidate statements first.
    """

    cleaned = clean_retrieved_text(text)
    candidates: list[str] = []

    for paragraph in split_paragraphs(cleaned):
        if is_noise_paragraph(paragraph):
            continue
        if looks_like_table_row(paragraph):
            candidates.extend(candidates_from_table_row(paragraph))
            continue
        candidates.extend(split_sentences(paragraph))

    return [candidate for candidate in candidates if len(candidate) >= 20 and not is_noise_sentence(candidate)]


def clean_retrieved_text(text: str) -> str:
    text = re.sub(r"^\s*---\s*$.*?^\s*---\s*$", " ", text, flags=re.MULTILINE | re.DOTALL)
    lines: list[str] = []
    skip_controlled_block = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        heading = re.sub(r"^\s{0,3}#{1,6}\s+", "", line).strip()
        if CONTROLLED_SECTION_RE.match(heading):
            skip_controlled_block = True
            continue
        if line.startswith("#"):
            skip_controlled_block = False
            continue
        if not line:
            skip_controlled_block = False
            lines.append("")
            continue
        if skip_controlled_block and (METADATA_LINE_RE.match(line) or looks_like_table_row(line)):
            continue
        if METADATA_LINE_RE.match(line) or TABLE_SEPARATOR_RE.match(line):
            continue
        lines.append(line)

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\[([^\]]+)]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", cleaned)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def split_paragraphs(text: str) -> list[str]:
    paragraphs = [paragraph.strip(" -") for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
    normalized: list[str] = []
    for paragraph in paragraphs:
        lines = [line.strip(" -") for line in paragraph.splitlines() if line.strip()]
        if not lines:
            continue
        if all(looks_like_table_row(line) for line in lines):
            normalized.extend(lines)
        else:
            normalized.append(" ".join(lines))
    return normalized


def looks_like_table_row(text: str) -> bool:
    return text.count("|") >= 2


def candidates_from_table_row(row: str) -> list[str]:
    cells = [cell.strip() for cell in row.strip("|").split("|")]
    cells = [cell for cell in cells if cell and not re.fullmatch(r":?-{3,}:?", cell)]
    if len(cells) < 2:
        return []
    if all(len(cell.split()) <= 5 for cell in cells):
        return []
    return [". ".join(cells).rstrip(".") + "."]


def is_noise_paragraph(paragraph: str) -> bool:
    lowered = paragraph.lower()
    if len(token_set(paragraph)) < 4:
        return True
    if lowered.count(";") >= 6 and any(marker in lowered for marker in ("keywords", "document code", "business area")):
        return True
    return False


def is_noise_sentence(sentence: str) -> bool:
    lowered = normalize_for_dedupe(sentence)
    if METADATA_LINE_RE.match(sentence):
        return True
    if lowered.startswith(("bsf-", "fuentes:", "source:", "keywords ", "document code ")):
        return True
    if lowered.count(";") >= 5:
        return True
    if len(sentence) > 420:
        return True
    if re.search(r"\b(document code|document title|business area|functional approver)\b", lowered):
        return True
    return False


def has_intent_phrase(query_terms: set[str], sentence: str) -> bool:
    normalized_sentence = normalize_for_dedupe(sentence)
    if {"temperatura", "temperaturas", "frio", "congelado", "cold", "chain"} & query_terms:
        return any(term in normalized_sentence for term in ("temperature", "temperatura", "cold chain", "congel"))
    if {"smeta"} & query_terms:
        return any(term in normalized_sentence for term in ("smeta", "sedex", "ethical trade", "audit"))
    if {"seguridad", "responsabilidades", "responsabilidad"} & query_terms:
        return any(term in normalized_sentence for term in ("responsib", "security", "seguridad", "hse"))
    return False


def candidate_quality_bonus(sentence: str) -> float:
    lowered = normalize_for_dedupe(sentence)
    bonus = 0.0
    if any(marker in lowered for marker in ("quick answer", "respuesta rapida", "in summary", "means", "is defined as")):
        bonus += 0.18
    if any(marker in lowered for marker in ("must", "should", "debe", "deben", "responsible", "responsabilidad")):
        bonus += 0.08
    if 60 <= len(sentence) <= 260:
        bonus += 0.05
    return bonus


def dedupe_sentences(
    ranked: list[tuple[float, str]],
    *,
    max_sentences: int,
) -> list[str]:
    selected: list[str] = []
    seen: set[str] = set()
    for _, sentence in ranked:
        normalized = normalize_for_dedupe(sentence)
        if normalized in seen:
            continue
        selected.append(sentence)
        seen.add(normalized)
        if len(selected) >= max_sentences:
            break

    return selected


def split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"^\s{0,3}#{1,6}\s+.+$", " ", text.strip(), flags=re.MULTILINE)
    normalized = re.sub(r"\s+", " ", normalized)
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    return [part.strip(" -") for part in parts if len(part.strip()) >= 20]


def format_answer(sentences: list[str]) -> str:
    if len(sentences) <= 2:
        return " ".join(sentences)
    return "\n".join(f"- {sentence}" for sentence in sentences)


def ensure_source_citation(sentence: str, source_label: str) -> str:
    sentence = sentence.rstrip()
    if re.search(r"\[S\d+\]$", sentence):
        return sentence
    return f"{sentence} [{source_label}]"


def build_answer_sources(
    results: list[SearchResult],
    *,
    allowed_labels: set[str] | None = None,
) -> list[AnswerSource]:
    sources: list[AnswerSource] = []
    seen_labels: set[str] = set()

    for result in results:
        if allowed_labels is not None and result.source_label not in allowed_labels:
            continue
        if result.source_label in seen_labels:
            continue
        metadata = result.chunk.metadata
        sources.append(
            AnswerSource(
                source_label=result.source_label,
                document_code=str(metadata.get("document_code", result.chunk.document_id)),
                title=str(metadata.get("title", "Untitled")),
                filename=str(metadata.get("filename", metadata.get("path", result.chunk.document_id))),
                section=str(metadata.get("section", "N/A")),
                category=str(metadata.get("category", "N/A")),
                owner=str(metadata.get("owner", "")),
                score=result.score,
            )
        )
        seen_labels.add(result.source_label)

    return sources


def source_labels_in(sentences: list[str]) -> set[str]:
    labels: set[str] = set()
    for sentence in sentences:
        labels.update(re.findall(r"\[(S\d+)\]", sentence))
    return labels


def infer_area(retrieved: RetrievalContext) -> str:
    if retrieved.applied_filters.get("category"):
        return retrieved.applied_filters["category"]
    if retrieved.results:
        return str(retrieved.results[0].chunk.metadata.get("category", ""))
    return ""


def infer_owner(
    retrieved: RetrievalContext,
    area_contacts: dict[str, str],
    area: str,
) -> str:
    for result in retrieved.results:
        owner = str(result.chunk.metadata.get("owner", "")).strip()
        if owner:
            return owner
    return area_contacts.get(area, "")


def token_set(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


def normalize_for_dedupe(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())
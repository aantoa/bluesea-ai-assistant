from __future__ import annotations

import re
from pathlib import Path

from rag_bsf.config import VECTOR_INDEX_FILE
from rag_bsf.embeddings import HashingEmbedder, TOKEN_RE
from rag_bsf.schemas import RetrievalContext, SearchResult
from rag_bsf.vector_store import LocalVectorStore


DEFAULT_CANDIDATE_K = 20
DEFAULT_TOP_K = 5
SEMANTIC_WEIGHT = 0.65
RERANK_WEIGHT = 0.35
LEXICAL_CANDIDATE_MULTIPLIER = 2
QUERY_EXPANSIONS = {
    "cuantos": "how much entitlement allowance available",
    "dias": "days entitlement allowance",
    "vacaciones": "licencia remunerada descanso dias habiles paid leave annual leave entitlement how much",
    "vacacion": "licencia remunerada descanso dias habiles paid leave annual leave entitlement how much",
    "licencia": "paid leave licencia remunerada descanso",
    "beneficio": "benefit benefits employee benefits company-provided benefits statutory benefits eligibility eligible employee support",
    "beneficios": "benefit benefits employee benefits company-provided benefits statutory benefits eligibility eligible employee support",
    "empleado": "employee eligible employee employment category human resources",
    "empleados": "employees eligible employees employment category human resources",
    "reembolso": "gastos costos expense reimbursement",
    "gasto": "reembolso costos expense reimbursement",
    "onboarding": "induccion incorporacion primer dia mandatory training",
    "induccion": "onboarding incorporacion primer dia mandatory training",
}


def retrieve_context(
    question: str,
    *,
    top_k: int = DEFAULT_TOP_K,
    candidate_k: int = DEFAULT_CANDIDATE_K,
    metadata_filters: dict[str, str] | None = None,
    index_file: Path = VECTOR_INDEX_FILE,
) -> RetrievalContext:
    """Retrieve and rerank chunks, then assemble the prompt context block."""

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")
    if candidate_k <= 0:
        raise ValueError("candidate_k must be greater than zero.")

    filters = normalize_metadata_filters(metadata_filters or {})
    embedder = HashingEmbedder()
    store = LocalVectorStore(index_file)
    store.load()

    if len(store) == 0:
        return RetrievalContext(
            question=question,
            context="",
            results=[],
            applied_filters=filters,
            candidate_count=0,
            filtered_count=0,
        )

    broad_k = max(top_k, candidate_k)
    expanded_question = expand_query(question)
    semantic_results = store.search(embedder.embed(expanded_question), top_k=broad_k)
    lexical_results = lexical_candidate_results(
        expanded_question,
        store.all_results(),
        top_k=max(broad_k, top_k * LEXICAL_CANDIDATE_MULTIPLIER),
    )
    candidate_results = merge_results(semantic_results, lexical_results)
    filtered_results = [result for result in candidate_results if metadata_matches(result, filters)]
    informative_results = [
        result for result in filtered_results if is_informative_chunk(result.chunk.text)
    ]
    rerank_input = informative_results or filtered_results
    reranked_results = rerank_results(expanded_question, rerank_input)[:top_k]
    relabel_results(reranked_results)

    return RetrievalContext(
        question=question,
        context=assemble_context(reranked_results),
        results=reranked_results,
        applied_filters=filters,
        candidate_count=len(candidate_results),
        filtered_count=len(filtered_results),
    )


def normalize_metadata_filters(filters: dict[str, str]) -> dict[str, str]:
    return {
        key.strip(): value.strip()
        for key, value in filters.items()
        if key and key.strip() and value and value.strip()
    }


def expand_query(question: str) -> str:
    additions: list[str] = []
    terms = token_set(question)
    for term in terms:
        expansion = QUERY_EXPANSIONS.get(term)
        if expansion:
            additions.append(expansion)
    if not additions:
        return question
    return " ".join([question, *additions])


def metadata_matches(result: SearchResult, filters: dict[str, str]) -> bool:
    if not filters:
        return True

    metadata = result.chunk.metadata
    for key, expected_value in filters.items():
        actual_value = metadata.get(key, "")
        if normalize_lookup_value(str(actual_value)) != normalize_lookup_value(expected_value):
            return False
    return True


def is_informative_chunk(text: str) -> bool:
    """Return False for chunks that only contain a heading or extraction noise."""

    body_without_headings = re.sub(r"^\s{0,3}#{1,6}\s+.+$", " ", text, flags=re.MULTILINE)
    body_without_rules = re.sub(r"^\s*-{3,}\s*$", " ", body_without_headings, flags=re.MULTILINE)
    tokens = TOKEN_RE.findall(body_without_rules)
    return len(tokens) >= 6


def rerank_results(question: str, results: list[SearchResult]) -> list[SearchResult]:
    reranked: list[SearchResult] = []
    for result in results:
        semantic_score = result.score
        rerank_score = lexical_relevance(question, result)
        final_score = (SEMANTIC_WEIGHT * semantic_score) + (RERANK_WEIGHT * rerank_score)
        reranked.append(
            SearchResult(
                chunk=result.chunk,
                score=final_score,
                source_label=result.source_label,
                semantic_score=semantic_score,
                rerank_score=rerank_score,
            )
        )

    return sorted(
        reranked,
        key=lambda item: (
            item.score,
            item.semantic_score or 0.0,
            item.rerank_score or 0.0,
        ),
        reverse=True,
    )


def lexical_candidate_results(
    question: str,
    results: list[SearchResult],
    *,
    top_k: int,
) -> list[SearchResult]:
    """Select textually relevant chunks so exact FAQ-style matches are not missed."""

    ranked: list[SearchResult] = []
    for result in results:
        score = lexical_relevance(question, result)
        if score <= 0:
            continue
        ranked.append(
            SearchResult(
                chunk=result.chunk,
                score=score,
                source_label=result.source_label,
                semantic_score=result.semantic_score,
                rerank_score=score,
            )
        )

    ranked.sort(key=lambda result: result.score, reverse=True)
    return ranked[:top_k]


def merge_results(*groups: list[SearchResult]) -> list[SearchResult]:
    """Merge candidate groups, keeping the strongest score for each chunk."""

    merged: dict[str, SearchResult] = {}
    for group in groups:
        for result in group:
            existing = merged.get(result.chunk.chunk_id)
            if existing is None or result.score > existing.score:
                merged[result.chunk.chunk_id] = result
    return list(merged.values())


def lexical_relevance(question: str, result: SearchResult) -> float:
    query_terms = token_set(question)
    if not query_terms:
        return 0.0

    metadata = result.chunk.metadata
    searchable_text = " ".join(
        [
            result.chunk.text,
            str(metadata.get("title", "")),
            str(metadata.get("section", "")),
            str(metadata.get("keywords", "")),
            str(metadata.get("category", "")),
        ]
    )
    chunk_terms = token_set(searchable_text)
    if not chunk_terms:
        return 0.0

    overlap = len(query_terms & chunk_terms) / len(query_terms)
    phrase_bonus = phrase_match_bonus(question, searchable_text)
    intent_bonus = intent_match_bonus(query_terms, searchable_text)
    return min(1.0, overlap + phrase_bonus + intent_bonus)


def token_set(text: str) -> set[str]:
    return {normalize_lookup_value(token) for token in TOKEN_RE.findall(text)}


def phrase_match_bonus(question: str, text: str) -> float:
    normalized_question = normalize_space(question)
    normalized_text = normalize_space(text)
    if not normalized_question or normalized_question not in normalized_text:
        return 0.0
    return 0.15


def intent_match_bonus(query_terms: set[str], text: str) -> float:
    """Boost chunks that answer common business-question intents directly."""

    normalized_text = normalize_space(text)
    bonus = 0.0

    vacation_terms = {"vacaciones", "vacacion", "annual", "leave", "entitlement"}
    quantity_terms = {"cuantos", "dias", "how", "much", "days"}
    if query_terms & vacation_terms and query_terms & quantity_terms:
        if "how much annual leave" in normalized_text:
            bonus += 0.35
        if "annual leave" in normalized_text and "entitlement" in normalized_text:
            bonus += 0.25
        if "leave and absence" in normalized_text and len(normalized_text) < 80:
            bonus -= 0.25

    benefit_terms = {
        "beneficio",
        "beneficios",
        "benefit",
        "benefits",
        "employee",
        "empleado",
        "empleados",
    }
    if query_terms & benefit_terms:
        if "employee benefits" in normalized_text:
            bonus += 0.30
        if "benefits and employee support" in normalized_text:
            bonus += 0.25
        if "where can i find information about employee benefits" in normalized_text:
            bonus += 0.35
        if "when do my benefits begin" in normalized_text:
            bonus += 0.30
        if "benefit eligibility" in normalized_text:
            bonus += 0.25
        if "leave and benefits policy" in normalized_text:
            bonus += 0.20
        if "can temporary employees access benefits" in normalized_text:
            bonus += 0.15
        irrelevant_hr_markers = (
            "what should i do if i will be late",
            "can i report a concern confidentially",
            "what should i do if i believe my pay is incorrect",
            "temporary and emergency access",
        )
        if any(marker in normalized_text for marker in irrelevant_hr_markers):
            bonus -= 0.35

    return bonus


def assemble_context(results: list[SearchResult]) -> str:
    blocks: list[str] = []
    for result in results:
        metadata = result.chunk.metadata
        header = (
            f"[{result.source_label}] "
            f"{metadata.get('document_code', result.chunk.document_id)} | "
            f"{metadata.get('title', 'Untitled')} | "
            f"section={metadata.get('section', 'N/A')} | "
            f"category={metadata.get('category', 'N/A')} | "
            f"review_date={metadata.get('review_date', 'N/A')}"
        )
        blocks.append(f"{header}\n{result.chunk.text.strip()}")
    return "\n\n---\n\n".join(blocks)


def relabel_results(results: list[SearchResult]) -> None:
    for idx, result in enumerate(results, start=1):
        result.source_label = f"S{idx}"


def normalize_lookup_value(value: str) -> str:
    normalized = value.strip().lower()
    normalized = normalized.replace("&", "and")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())

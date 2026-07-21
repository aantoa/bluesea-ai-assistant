from rag_bsf.answer_generation import build_answer_prompt, generate_grounded_answer
from rag_bsf.schemas import Chunk, RetrievalContext, SearchResult


def _retrieved_context(score=0.82):
    result = SearchResult(
        chunk=Chunk(
            chunk_id="BSF-HR-003::chunk-0001",
            document_id="BSF-HR-003",
            text=(
                "La licencia remunerada anual otorga veinte dias habiles de descanso. "
                "El colaborador debe coordinar la programacion con Recursos Humanos."
            ),
            metadata={
                "document_code": "BSF-HR-003",
                "title": "Leave and Benefits Policy",
                "filename": "BSF-HR-003_Leave_and_Benefits_Policy.docx",
                "category": "Human Resources",
                "section": "Paid Leave",
                "owner": "Human Resources Manager",
            },
        ),
        score=score,
        source_label="S1",
        semantic_score=score,
        rerank_score=0.7,
    )
    return RetrievalContext(
        question="cuantos dias de vacaciones tengo",
        context=(
            "[S1] BSF-HR-003 | Leave and Benefits Policy | section=Paid Leave | "
            "category=Human Resources | review_date=N/A\n"
            "La licencia remunerada anual otorga veinte dias habiles de descanso."
        ),
        results=[result],
        candidate_count=1,
        filtered_count=1,
    )


def test_build_answer_prompt_restricts_model_to_retrieved_context():
    prompt = build_answer_prompt("pregunta", "[S1] contexto")

    assert "Responde unicamente con base en el CONTEXTO RECUPERADO" in prompt
    assert "No uses conocimiento externo" in prompt
    assert "[S1] contexto" in prompt


def test_generate_grounded_answer_includes_citations_and_sources():
    answer = generate_grounded_answer(
        "cuantos dias de vacaciones tengo",
        _retrieved_context(),
        min_confidence=0.2,
    )

    assert answer.grounded
    assert "veinte dias habiles" in answer.answer
    assert "[S1]" in answer.answer
    assert "Fuentes:" in answer.answer
    assert answer.sources[0].filename == "BSF-HR-003_Leave_and_Benefits_Policy.docx"
    assert answer.sources[0].section == "Paid Leave"


def test_generate_grounded_answer_falls_back_without_context():
    answer = generate_grounded_answer(
        "cual es el bono anual",
        RetrievalContext(question="cual es el bono anual", context="", results=[]),
    )

    assert not answer.grounded
    assert answer.fallback_reason == "no_retrieved_context"
    assert "No encontre esta informacion" in answer.answer
    assert answer.sources == []


def test_generate_grounded_answer_falls_back_with_low_confidence():
    answer = generate_grounded_answer(
        "cual es el bono anual",
        _retrieved_context(score=0.05),
        min_confidence=0.2,
    )

    assert not answer.grounded
    assert answer.fallback_reason == "low_retrieval_confidence"
    assert "No encontre esta informacion" in answer.answer

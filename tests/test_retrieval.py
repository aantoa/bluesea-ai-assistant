from rag_bsf.embeddings import HashingEmbedder
from rag_bsf.retrieval import (
    assemble_context,
    expand_query,
    is_informative_chunk,
    lexical_candidate_results,
    metadata_matches,
    retrieve_context,
)
from rag_bsf.schemas import Chunk, SearchResult
from rag_bsf.vector_store import LocalVectorStore


def _build_index(index_path):
    embedder = HashingEmbedder(dimensions=32)
    store = LocalVectorStore(index_path)
    chunks = [
        Chunk(
            chunk_id="BSF-HR-001::chunk-0001",
            document_id="BSF-HR-001",
            text="La licencia remunerada anual otorga veinte dias habiles de descanso.",
            metadata={
                "document_code": "BSF-HR-001",
                "title": "Employee Handbook",
                "category": "Human Resources",
                "section": "Paid Leave",
                "review_date": "2026-01-07",
            },
        ),
        Chunk(
            chunk_id="BSF-OPS-001::chunk-0001",
            document_id="BSF-OPS-001",
            text="El control de cadena de frio se verifica durante recepcion y despacho.",
            metadata={
                "document_code": "BSF-OPS-001",
                "title": "Cold Chain Procedure",
                "category": "Operations",
                "section": "Temperature Control",
            },
        ),
    ]
    for chunk in chunks:
        store.add(
            chunk=chunk,
            vector=embedder.embed(chunk.text),
            embedding_model=embedder.model_name,
            dimensions=embedder.dimensions,
        )
    store.save()


def test_metadata_matches_exact_normalized_values():
    result = SearchResult(
        chunk=Chunk(
            chunk_id="1",
            document_id="1",
            text="Texto",
            metadata={"category": "Human Resources"},
        ),
        score=0.9,
        source_label="S1",
    )

    assert metadata_matches(result, {"category": "human resources"})
    assert not metadata_matches(result, {"category": "Operations"})


def test_expand_query_adds_corporate_synonyms():
    expanded = expand_query("cuantos dias de vacaciones tengo")

    assert "licencia remunerada" in expanded
    assert "how much" in expanded
    assert "paid leave" in expanded


def test_is_informative_chunk_rejects_heading_only_chunks():
    assert not is_informative_chunk("# 8. Leave and Absence\n\n---")
    assert is_informative_chunk(
        "## 8.2 How much annual leave do I have?\n\n"
        "Your entitlement depends on applicable law and company policy."
    )

def test_lexical_candidates_include_direct_annual_leave_answer():
    results = [
        SearchResult(
            chunk=Chunk(
                chunk_id="generic",
                document_id="BSF-HR-003",
                text="The policy covers annual leave, sick leave, benefits, payroll and records.",
                metadata={
                    "document_code": "BSF-HR-003",
                    "title": "Leave and Benefits Policy",
                    "category": "Human Resources",
                    "section": "Document",
                },
            ),
            score=0.9,
            source_label="S1",
        ),
        SearchResult(
            chunk=Chunk(
                chunk_id="direct",
                document_id="BSF-HR-002",
                text=(
                    "## 8.2 How much annual leave do I have?\n\n"
                    "Your entitlement depends on applicable law, employment conditions, and company policy."
                ),
                metadata={
                    "document_code": "BSF-HR-002",
                    "title": "Employee FAQ",
                    "category": "Human Resources",
                    "section": "8.2 How much annual leave do I have?",
                },
            ),
            score=0.1,
            source_label="S2",
        ),
    ]

    candidates = lexical_candidate_results(
        expand_query("cuantos dias de vacaciones tengo"),
        results,
        top_k=1,
    )

    assert candidates[0].chunk.chunk_id == "direct"


def test_retrieve_context_filters_reranks_and_assembles_context(tmp_path):
    index_path = tmp_path / "vectors.jsonl"
    _build_index(index_path)

    retrieved = retrieve_context(
        "cuantos dias de vacaciones tengo",
        top_k=1,
        candidate_k=2,
        metadata_filters={"category": "Human Resources"},
        index_file=index_path,
    )

    assert retrieved.candidate_count == 2
    assert retrieved.filtered_count == 1
    assert len(retrieved.results) == 1
    assert retrieved.results[0].chunk.document_id == "BSF-HR-001"
    assert retrieved.results[0].source_label == "S1"
    assert "BSF-HR-001 | Employee Handbook" in retrieved.context


def test_assemble_context_includes_source_metadata():
    result = SearchResult(
        chunk=Chunk(
            chunk_id="BSF-HR-001::chunk-0001",
            document_id="BSF-HR-001",
            text="Texto recuperado.",
            metadata={
                "document_code": "BSF-HR-001",
                "title": "Employee Handbook",
                "category": "Human Resources",
                "section": "Paid Leave",
            },
        ),
        score=0.8,
        source_label="S1",
    )

    context = assemble_context([result])

    assert "[S1] BSF-HR-001 | Employee Handbook" in context
    assert "Texto recuperado." in context

import json

from rag_bsf.embeddings import HashingEmbedder, cosine_similarity
from rag_bsf.rag_pipeline import index_chunks, load_chunks, search_index
from rag_bsf.schemas import Chunk
from rag_bsf.vector_store import LocalVectorStore


def test_hashing_embedder_is_deterministic_and_normalized():
    embedder = HashingEmbedder(dimensions=32)

    first = embedder.embed("politica de reembolso de gastos")
    second = embedder.embed("politica de reembolso de gastos")

    assert first == second
    assert len(first) == 32
    assert round(cosine_similarity(first, first), 6) == 1.0


def test_hashing_embedder_returns_zero_vector_for_empty_text():
    embedder = HashingEmbedder(dimensions=16)

    vector = embedder.embed("")

    assert vector == [0.0] * 16


def test_local_vector_store_saves_loads_and_searches(tmp_path):
    index_path = tmp_path / "vectors.jsonl"
    chunk = Chunk(
        chunk_id="BSF-FIN-001::chunk-0001",
        document_id="BSF-FIN-001",
        text="Politica de reembolso de gastos corporativos.",
        metadata={"document_code": "BSF-FIN-001", "title": "Expense Policy"},
    )
    embedder = HashingEmbedder(dimensions=32)
    store = LocalVectorStore(index_path)
    store.add(
        chunk=chunk,
        vector=embedder.embed(chunk.text),
        embedding_model=embedder.model_name,
        dimensions=embedder.dimensions,
    )
    store.save()

    loaded_store = LocalVectorStore(index_path)
    loaded_store.load()
    results = loaded_store.search(embedder.embed("reembolso de costos"), top_k=1)

    assert len(loaded_store) == 1
    assert results[0].chunk.chunk_id == "BSF-FIN-001::chunk-0001"
    assert results[0].source_label == "S1"


def test_index_chunks_generates_vector_file_and_manifest(tmp_path):
    chunks_file = tmp_path / "chunks.jsonl"
    index_file = tmp_path / "vectors.jsonl"
    manifest_file = tmp_path / "embeddings_manifest.json"
    chunk = Chunk(
        chunk_id="BSF-HR-001::chunk-0001",
        document_id="BSF-HR-001",
        text="Los colaboradores deben revisar el codigo de conducta.",
        metadata={"document_code": "BSF-HR-001", "title": "Employee Handbook"},
    )
    chunks_file.write_text(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n", encoding="utf-8")

    stats = index_chunks(
        chunks_file=chunks_file,
        index_file=index_file,
        manifest_file=manifest_file,
    )

    assert stats["chunks"] == 1
    assert stats["vectors"] == 1
    assert index_file.exists()
    assert manifest_file.exists()
    assert load_chunks(chunks_file)[0].chunk_id == "BSF-HR-001::chunk-0001"

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest["embedding_model"] == "local-hashing-v1"
    assert manifest["chunks"] == 1
    assert manifest["vectors"] == 1

    results = search_index("codigo de conducta", top_k=1, index_file=index_file)
    assert results[0].chunk.document_id == "BSF-HR-001"
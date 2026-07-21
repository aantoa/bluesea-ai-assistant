from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag_bsf.rag_pipeline import retrieve_rag_context


if __name__ == "__main__":
    question = "cuantos dias de vacaciones tengo"
    retrieved = retrieve_rag_context(question, top_k=5, candidate_k=20)
    print(retrieved.context)
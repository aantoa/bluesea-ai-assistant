from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag_bsf.rag_pipeline import answer_question


if __name__ == "__main__":
    question = "cuantos dias de vacaciones tengo"
    result = answer_question(question, top_k=5, candidate_k=20)
    print(result.answer)

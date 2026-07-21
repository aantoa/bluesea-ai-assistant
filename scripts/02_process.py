from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag_bsf.rag_pipeline import process_documents


if __name__ == "__main__":
    stats = process_documents()
    print(
        "Processing completed: "
        f"{stats['documents']} documents, {stats['chunks']} chunks."
    )
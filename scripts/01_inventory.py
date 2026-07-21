from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag_bsf.rag_pipeline import build_inventory


if __name__ == "__main__":
    inventory = build_inventory()
    print(f"Inventory created with {len(inventory)} documents.")
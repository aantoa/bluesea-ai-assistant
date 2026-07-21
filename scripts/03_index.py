from rag_bsf.rag_pipeline import index_chunks


if __name__ == "__main__":
    stats = index_chunks()
    print(stats)
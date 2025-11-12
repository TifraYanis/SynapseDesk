import os
import json
import argparse
import re
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm

def tokenize(s: str):
    """Nettoyage simple pour BM25 corpus."""
    return re.findall(r"[a-zA-Z0-9_]+", s.lower())

def build_hybrid_index(corpus_path: str, index_dir: str, model_name: str = "intfloat/multilingual-e5-base", batch_size: int = 64):
    os.makedirs(index_dir, exist_ok=True)

    # --- Lecture du corpus JSONL généré par ingest_data.py ---
    records = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not records:
        print(f"Aucun document trouvé dans {corpus_path}")
        return

    print(f"📚 Corpus chargé : {len(records)} documents")
    model = SentenceTransformer(model_name)

    # --- Encodage incrémental pour éviter OOM ---
    texts = [r["text"] for r in records]
    embs_list = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Encodage embeddings"):
        batch = texts[i:i+batch_size]
        embs = model.encode(batch, normalize_embeddings=True, convert_to_numpy=True)
        embs_list.append(embs)
    embs = np.vstack(embs_list).astype("float32")

    # --- Index dense (FAISS) ---
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs)
    faiss.write_index(index, os.path.join(index_dir, "dense.index"))

    # --- Corpus BM25 (texte brut) ---
    with open(os.path.join(index_dir, "bm25_corpus.txt"), "w", encoding="utf-8") as f:
        for r in records:
            f.write(" ".join(tokenize(r["text"])) + "\n")

    # --- Corpus JSONL complet pour le Retriever ---
    with open(os.path.join(index_dir, "corpus.jsonl"), "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("\nIndex hybride généré avec succès !")
    print(f"Documents indexés : {len(records)}")
    print(f"Dimension des embeddings : {dim}")
    print(f"Dossier index : {index_dir}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="./api/output/corpus.jsonl")
    ap.add_argument("--index_dir", default="./indices")
    ap.add_argument("--model", default="intfloat/multilingual-e5-base")
    args = ap.parse_args()

    build_hybrid_index(args.corpus, args.index_dir, args.model)

if __name__ == "__main__":
    main()

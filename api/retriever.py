import os, json, re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi

def tokenize(s: str):
    return re.findall(r"[a-zA-Z0-9_]+", s.lower())

class Retriever:
    def __init__(self, index_dir="./indices",
                 embed_model="intfloat/multilingual-e5-base",
                 cross_model="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.index_dir = index_dir
        self.embed = SentenceTransformer(embed_model)
        self.cross = CrossEncoder(cross_model)
        self.faiss = faiss.read_index(os.path.join(index_dir, "dense.index"))
        
        # Load corpus
        self.records = []
        with open(os.path.join(index_dir, "corpus.jsonl"), encoding="utf-8") as f:
            for line in f:
                self.records.append(json.loads(line))
        print(f"[Retriever] Corpus chargé : {len(self.records)} passages")

        # BM25
        with open(os.path.join(index_dir, "bm25_corpus.txt"), encoding="utf-8") as f:
            tokenized = [line.strip().split() for line in f]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query, topk_dense=15, topk_bm25=15, rerank_topk=8):
        qv = self.embed.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")

        # Dense retrieval
        scores_d, ids_d = self.faiss.search(qv, topk_dense)
        dense_hits = [int(i) for i in ids_d[0] if i != -1]

        # BM25 retrieval
        bm25_scores = self.bm25.get_scores(tokenize(query))
        bm25_hits = list(np.argsort(bm25_scores)[::-1][:topk_bm25])

        # Combine
        # candidate_ids = list(dict.fromkeys(dense_hits + bm25_hits))
        combined = {}
        for i, cid in enumerate(dense_hits): combined[cid] = combined.get(cid, 0) + (10 - i)
        for i, cid in enumerate(bm25_hits): combined[cid] = combined.get(cid, 0) + (10 - i)
        candidate_ids = sorted(combined, key=combined.get, reverse=True)[:30]
        
        print(f"[Retriever] {len(candidate_ids)} candidats avant rerank.")

        if not candidate_ids:
            return []

        # Rerank (cross-encoder)
        pairs = [(query, self.records[i]["text"]) for i in candidate_ids]
        rerank_scores = self.cross.predict(pairs)

        scored = [
            {
                "id": cid,
                "score": float(rerank_scores[i]),
                "text": self.records[cid]["text"],
                "path": self.records[cid]["path"]
            }
            for i, cid in enumerate(candidate_ids)
        ]

        scored = sorted(scored, key=lambda x: x["score"], reverse=True)[:rerank_topk]
        print(f"[Retriever] Top {len(scored)} résultats après rerank.")
        return scored

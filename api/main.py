from fastapi import FastAPI
from pydantic import BaseModel
import os, yaml, json

from api.retriever import Retriever
from api.llm_manager import generate_with_ollama


class QueryRequest(BaseModel):
    query: str


app = FastAPI(title="RAG Ops Copilot (Ollama)")

# Chargement de la configuration
with open(os.path.join("configs", "settings.yaml"), "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

retriever = None


@app.on_event("startup")
def startup():
    """Initialise le retriever FAISS + BM25 + re-ranking"""
    global retriever
    retriever = Retriever(
        index_dir=cfg["index_dir"],
        embed_model=cfg["embedding_model"],
        cross_model=cfg["cross_encoder_model"]
    )


@app.get("/health")
def health():
    """Test de santé"""
    return {"status": "ok"}


@app.post("/query")
def query(req: QueryRequest):
    q = req.query
    hits = retriever.search(q, topk_dense=8, topk_bm25=8, rerank_topk=6)

    if not hits:
        # Aucun résultat RAG
        answer = generate_with_ollama(f"Réponds clairement à : {q}", max_tokens=512)
        return {"answer": answer, "citations": []}

    # Vérifie si les scores sont globalement faibles
    max_score = max(h["score"] for h in hits)
    # if max_score < 0.05:
    if max_score < 0.01 and "?" in q:
        answer = generate_with_ollama(f"Réponds clairement à : {q}", max_tokens=512)
        return {"answer": answer, "citations": []}

    # --- RAG actif ---
    ctx_text = "\n\n---\n\n".join([f"Source ({h['path']}):\n{h['text'][:1500]}" for h in hits])
    
    prompt = f"""
    Tu es un assistant spécialisé dans le support aux équipes techniques et fonctionnelles.
    Utilise les informations suivantes pour répondre à la question :
    {q}

    Contexte :
    {ctx_text}

    Structure ta réponse avec :
    - Résumé
    - Analyse
    - Recommandations concrètes
    - Sources (liste)
    """
    out = generate_with_ollama(prompt, max_tokens=512)
    citations = [
        {"source": h["path"], "score": round(h["score"], 3), "snippet": h["text"][:220].replace("\n", " ")}
        for h in hits
    ]
    return {"answer": out, "citations": citations}



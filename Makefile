.PHONY: setup ingest build-index ollama-check api streamlit run clean generate-data
# ======================================================
# 🧠 RAG Ops Copilot - Makefile (Pro Portfolio Edition)
# Author: Yanis Tifra
# ======================================================

# Chemins de base
PYTHON := .venv/Scripts/python
PIP := .venv/Scripts/pip
DATA_DIR = ./api/data
INDEX_DIR = ./indices
EMBED_MODEL = intfloat/multilingual-e5-base

# ======================================================
# 🔧 Setup complet
# ======================================================

setup:
	@echo "Création de l'environnement virtuel (Python 3.11)…"
	py -3.11 -m venv .venv
	.venv\Scripts\pip install -r requirements.txt
	@echo "Environnement configuré avec Python 3.11"


# ======================================================
# 📥 Ingestion et Indexation
# ======================================================

generate-data:
	@echo "Génération de données de test enrichies..."
	$(PYTHON) api/generate_rich_testdata.py
	@echo "Donnees synthetiques generees dans ./api/data"

ingest:
	@echo "Ingestion des données dans ./api/data..."
	$(PYTHON) api/ingest_data.py --data_dir ./api/data

build-index:
	@echo "Construction de l'index FAISS + BM25 à partir du corpus..."
	$(PYTHON) scripts/build_hybrid_index.py --corpus ./api/output/corpus.jsonl --index_dir $(INDEX_DIR) --model $(EMBED_MODEL)
	@echo "Index construit avec succès dans $(INDEX_DIR)"

reindex: ingest build-index

# ======================================================
# 🤖 Vérification Ollama
# ======================================================

ollama-run:
	@echo "Démarrage d'Ollama en tâche de fond..."
	@start /B ollama serve


ollama-check:
	@echo "Verification Ollama..."
	@curl http://localhost:11434/api/tags


# ======================================================
# 🚀 Lancement API & App
# ======================================================

api:
	@echo "Lancement de l'API FastAPI..."
	$(PYTHON) -m uvicorn api.main:app --reload

streamlit:
	@echo "Lancement de l'interface Streamlit..."
	$(PYTHON) -m streamlit run streamlit_app/app.py




# ======================================================
# ♻️ Maintenance
# ======================================================

restart:
	@echo "Redémarrage..."
	-taskkill /F /IM uvicorn.exe /T 2>nul || true
	-taskkill /F /IM streamlit.exe /T 2>nul || true
	make run

clean:
	@echo "Nettoyage..."
	@if exist $(INDEX_DIR) rmdir /S /Q $(INDEX_DIR)
	@if exist .venv rmdir /S /Q .venv
	@echo "Nettoyage terminé."

update:
	@echo "Mise à jour des dépendances..."
	$(PIP) install --upgrade -r requirements.txt

# 🧠 SynapseDesk — Copilote RAG local (Ollama + Mistral)

![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-FF4B4B.svg)
![Ollama](https://img.shields.io/badge/Ollama-Mistral_7B-lightgrey.svg)
![FAISS](https://img.shields.io/badge/FAISS-BM25%20Hybrid-orange.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 🚀 Présentation du projet

**SynapseDesk** est un copilote d’entreprise local conçu pour aider les équipes **Data, IT, RH, DevOps ou métiers**.  
Il connecte vos **données internes (docs, logs, fiches, tickets)** à un **LLM local (Mistral 7B via Ollama)** pour fournir :
- des **diagnostics techniques** (jobs Spark, configurations, logs),
- des **explications** claires sur des politiques ou procédures,
- des **réponses sourcées et contextualisées**,
- et des **analyses actionnables**.

🎯 **Objectif :** un assistant robuste, privé et directement exploitable en entreprise.

---
## 🎥 Démonstration visuelle

<p align="center">
  <img src="assets/pagedefilante.gif" alt="Démonstration du copilote RAG SynapseDesk" width="850">
</p>

---
## 🧩 Architecture

```
Utilisateur → Streamlit UI → FastAPI API → Retriever hybride (FAISS + BM25)
                                  ↳ Cross-Encoder (re-ranking)
                                  ↳ Mistral (Ollama) → Réponse structurée
```

### 🔹 Étapes principales
1. **Ingestion & Normalisation** : extraction texte depuis `api/data/` (md, txt, html, docx, json, code).  
2. **Indexation hybride** : génération d’embeddings (`intfloat/multilingual-e5-base`) + BM25 lexical.  
3. **Retrieval & Fusion** : recherche sémantique et lexicale, fusionnée par score.  
4. **Re-ranking** : reclassement précis via CrossEncoder.  
5. **Synthèse** : Mistral (via Ollama) produit une réponse claire, justifiée et citée.  
6. **Fallback automatique** : si `max_score < 0.01`, bascule en **chat libre** sans contexte.

---

## ⚙️ Stack technique

| Composant | Description |
|------------|-------------|
| 🧠 **LLM local** | Mistral 7B via Ollama (`localhost:11434`) |
| 🚀 **Backend API** | FastAPI (Python 3.11) |
| 🔍 **Retrieval** | FAISS (embeddings denses) + BM25 (lexical) |
| 🪄 **Re-ranking** | CrossEncoder (`ms-marco-MiniLM-L-6-v2`) |
| 💬 **Frontend** | Streamlit multipage (Copilot / Présentation / Tests) |
| 🗂️ **Indexation** | `scripts/build_hybrid_index.py` |
| 📚 **Ingestion** | `api/ingest_data.py` |
| 🧱 **Données simulées** | Logs Spark, fiches internes, FAQ, RH, tickets |

---

## 🧠 Logique adaptative

Le système évalue la pertinence des passages trouvés :
- Si le **score maximal** ≥ `0.01` → **RAG activé** (réponse sourcée à partir des données internes)
- Si le **score maximal** < `0.01` → **chat libre** (réponse générative du LLM)

> ⚖️ Cette logique évite les “hallucinations” et garantit que le modèle ne s’appuie que sur des sources fiables.

---

## 🧑‍💻 Installation et exécution

### 1️⃣ Cloner le dépôt
```bash
git clone https://github.com/TifraYanis/synapsedesk.git
cd synapsedesk
```

### 2️⃣ Créer l’environnement et installer les dépendances
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3️⃣ Générer les données et index
```bash
make generate-data    # crée des données internes simulées
make ingest           # convertit les fichiers en corpus.jsonl
make build-index      # crée les index FAISS + BM25
```

### 4️⃣ Lancer Ollama et télécharger Mistral
```bash
ollama pull mistral
ollama serve
```

### 5️⃣ Démarrer l’API et le front
```bash
make api
make streamlit
```

➡️ Application disponible sur : [http://localhost:8501](http://localhost:8501)

---

## 🖥️ Interface Streamlit

**3 onglets principaux :**
1. 💬 **Copilot** – Chat multi-conversation (RAG + citations internes)
2. 📘 **Présentation** – Architecture, pipeline, choix techniques détaillés
3. 🧪 **Tests** – Scénarios et cas de validation automatiques

---

## 🎨 Design

- Interface sombre élégante (`#0E1117 / #1E1E2E / #00FFB3`)
- Effet lumineux sur les titres et transitions fluides
- Citations pliables avec affichage des scores
- Responsive et épuré

---

## 🧩 Structure du projet

```
SYNAPSEDESK/
├── api/
│   ├── ingest_data.py       # Ingestion & nettoyage des fichiers
│   ├── retriever.py         # FAISS + BM25 + re-ranking
│   ├── llm_manager.py       # Interface Ollama
│   └── main.py              # FastAPI backend
├── scripts/
│   ├── build_hybrid_index.py
│   └── generate_data.py
├── indices/                 # Index FAISS + BM25 générés
├── streamlit_app/
│   ├── app.py
│   └── pages/
│       ├── 1_Copilot.py
│       ├── 2_Presentation.py
│       └── 3_Tests.py
├── configs/settings.yaml
├── Makefile
└── requirements.txt
```

---

## 📈 Exemple de réponse

**Question :** “Pourquoi mon job `bronze_to_silver` est lent ?”

```
Résumé : Probable saturation mémoire sur le stage 3.
Analyse : déséquilibre de partitions et jointures non broadcastées.
Actions : vérifier spark.sql.shuffle.partitions, filtrer les tables amont, utiliser broadcast join.
Sources : logs/log_0042.json, docs/Troubleshooting_Spark.md
```

---

## 🔮 Améliorations prévues

- 🧾 Support PDF + OCR (Tesseract)
- 🔁 Cache Redis pour accélérer le retrieval
- 📊 Dashboard d’analyse et monitoring
- 🧩 Historique multi-utilisateurs
- 🛡️ Guardrails (détection PII, sensibilité des données)

---

## 👤 Auteur

**Tifra Yanis**  
📍 Data / AI Engineer — France  
🔗 [LinkedIn](https://www.linkedin.com/in/yanis-tifra-969134204/)  
💻 [GitHub](https://github.com/TifraYanis)

---

## 📜 Licence

Sous licence **MIT**, libre de réutilisation et d’adaptation, avec attribution à l’auteur original.

```
MIT License © 2025 Tifra Yanis
```

---

## ⭐ Support & feedback

Si le projet t’a aidé :
- ⭐ Laisse une étoile sur GitHub  
- 🔁 Forke et adapte à ton environnement  
- 🧠 Mentionne-le sur ton portfolio ou LinkedIn (`#RAG #LLM #FastAPI #Streamlit #Mistral`)  

import os
import json
from pathlib import Path
import streamlit as st
import yaml

# --------------------------------
# Config page
# --------------------------------
st.set_page_config(page_title="Présentation", page_icon="📘", layout="wide")
st.markdown("<h2 class='page-title'>📘 Présentation du projet</h2>", unsafe_allow_html=True)

# Helper badge
def badge(text, color="#0ea5e9"):
    st.markdown(
        f"""
        <span style="
            display:inline-block;
            padding:4px 10px;
            border-radius:999px;
            background:{color};
            color:white;
            font-size:0.85rem;
            margin-right:8px;">{text}</span>
        """,
        unsafe_allow_html=True,
    )

# Charger settings.yaml si présent
settings_path = Path("configs/settings.yaml")
settings_text = settings_path.read_text(encoding="utf-8") if settings_path.exists() else "Fichier de config introuvable."
try:
    settings_yaml = yaml.safe_load(settings_text) if settings_path.exists() else {}
except Exception:
    settings_yaml = {}

# Résumé haut de page
with st.container():
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.write(
            """
            **SynapseDesk** est un RAG local qui connecte la connaissance interne de l'entreprise à un modèle de langage.
            L'objectif est de fournir des réponses pertinentes, sourcées et actionnables, en privilégiant d'abord vos données.
            """
        )
        badge("100% local")
        badge("RAG hybride")
        badge("Ollama + Mistral", "#10b981")
        badge("FAISS + BM25", "#8b5cf6")
        badge("Re-ranking CrossEncoder", "#f59e0b")
        st.caption("Techniques clés: FastAPI pour l'API, Streamlit pour le front de démo.")
    with col_r:
        st.metric("Corpus", value="api/output/corpus.jsonl", delta="indexé en FAISS+BM25")
        st.metric("LLM", value=os.getenv("OLLAMA_MODEL", "mistral:latest"))
        st.metric("Adaptation", value="RAG ou Chat libre")

st.divider()

# --------------------------------
# Onglets
# --------------------------------
tabs = st.tabs([
    "🔎 1. Vue d'ensemble",
    "🗂️ 2. Ingestion",
    "🧭 3. Indexation et Retrieval",
    "🎯 4. Re-ranking",
    "🧠 5. Synthèse LLM",
    "⚖️ 6. Logique d’adaptation",
    "🧪 7. Tests et Validation",
    "⚙️ 8. Configuration et Déploiement",
    "🗺️ 9. Schéma global",
])

# --------------------------------
# 1. Vue d'ensemble
# --------------------------------
with tabs[0]:
    st.subheader("Objectif du produit")
    st.markdown(
        """
        - Offrir un copilote interne pour les équipes Data, IT, RH, métiers et support.  
        - Répondre aux questions en **priorisant les sources d'entreprise**.  
        - Expliquer, diagnostiquer, proposer des **actions concrètes** et **citer les sources**.  
        """
    )

    st.subheader("Pipeline logique")
    st.markdown(
        """
        1. Ingestion de documents hétérogènes  
        2. Indexation hybride: embeddings denses (FAISS) et lexical (BM25)  
        3. Retrieval des candidats  
        4. Re-ranking par CrossEncoder  
        5. Construction du contexte et synthèse LLM  
        6. Adaptation: si pas de contexte pertinent, bascule en chat libre  
        """
    )

    st.subheader("🔍 Comprendre FAISS et BM25")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            **📘 FAISS (Facebook AI Similarity Search)**  
            - Librairie développée par Meta pour la **recherche vectorielle**.  
            - Permet de comparer des textes selon leur **proximité sémantique**,  
              c’est-à-dire le **sens global** plutôt que les mots exacts.  
            - Dans SynapseDesk, chaque passage de document est encodé en **vecteur numérique (embedding)**  
              via le modèle `intfloat/multilingual-e5-base`.  
            - FAISS permet ensuite de retrouver les passages **les plus proches** du sens de la question.  
            """
        )
    with col2:
        st.markdown(
            """
            **📗 BM25 (Best Matching 25)**  
            - Méthode classique de **recherche lexicale** issue du monde des moteurs de recherche (Okapi BM25).  
            - Elle compare la **fréquence et la rareté** des mots d’une requête dans chaque document.  
            - Très utile pour les **termes techniques exacts, acronymes, noms de jobs ou scripts internes**.  
            - Dans SynapseDesk, BM25 complète FAISS en apportant une vision **mots-clés et fréquence**.  
            - En combinant FAISS + BM25, on obtient une **recherche hybride** :  
              robuste aux reformulations et sensible aux termes exacts.  
            """
        )

    with st.expander("Pourquoi ce design"):
        st.write(
            """
            - BM25 est robuste aux mots clés, acronymes et fautes mineures.  
            - FAISS capture la similarité sémantique et les paraphrases.  
            - Le CrossEncoder rerank les candidats en tenant compte de la question.  
            - Le LLM reste au service des données internes.  
            - La bascule en chat libre évite d'injecter du bruit si les scores sont faibles.  
            """
        )

# ------------------------------
# 2. Ingestion des données internes
# ------------------------------
with tabs[1]:
    st.subheader("Rôle de l’ingestion")
    st.markdown(
        """
        L’étape d’ingestion transforme les différentes sources internes de l’entreprise
        (documents, logs, notes, codes) en un corpus unifié et exploitable pour le moteur de recherche.

        Cette phase est réalisée par le script **`api/ingest_data.py`**, qui :
        - parcourt le dossier `api/data/`,
        - lit et convertit plusieurs formats (Markdown, TXT, HTML, DOCX, JSON, code Python),
        - nettoie les balises et métadonnées inutiles,
        - sauvegarde le tout dans un corpus **`api/output/corpus.jsonl`** utilisable par la suite.
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Structure des données**")
        st.code(
            """
            api/
              data/
                Troubleshooting_Spark.md
                Onboarding_Policy.md
                Incident_OOM.docx
                Confluence_DataPlatform.txt
                log_0007.json
              output/
                corpus.jsonl
            """,
            language="text",
        )
        st.caption("Chaque ligne du corpus représente un document normalisé (texte brut + métadonnées).")

    with col2:
        st.markdown("**Extrait simplifié du code**")
        st.code(
            """
            for file in os.listdir(data_dir):
                if file.endswith(('.md', '.txt', '.docx', '.html', '.json')):
                    text = extract_text(file)
                    record = {"text": text, "path": file}
                    corpus.append(record)
            save_jsonl(corpus, "api/output/corpus.jsonl")
            """,
            language="python",
        )
        st.caption("Chaque fichier est lu, converti et ajouté au corpus unifié.")

    with st.expander("Bonnes pratiques d’ingestion"):
        st.write(
            """
            - Nettoyer les fichiers HTML avant ingestion.  
            - Supprimer les menus, bannières et métadonnées inutiles.  
            - Centraliser les exports Confluence, politiques RH et logs techniques.  
            - Identifier les formats non textuels (PDF, images OCR) pour les futurs ajouts.
            """
        )

    st.info(
        "💡 Cette étape ne réalise **pas de chunking** — chaque document est indexé dans son ensemble. "
        "Cela suffit pour les fichiers courts et moyens de ton corpus. "
        "Le découpage en chunks pourra être ajouté plus tard pour les documents longs (option d’amélioration).",
        icon="🧩"
    )


# --------------------------------
# 3. Indexation & Retrieval
# --------------------------------

with tabs[2]:
    st.subheader("Création de l’index hybride (FAISS + BM25)")
    st.markdown(
    """
    Cette étape est assurée par le script scripts/build_hybrid_index.py,
    qui lit le corpus api/output/corpus.jsonl (généré par l’ingestion) et produit
    deux structures d’index complémentaires :
    - un index FAISS pour la recherche vectorielle sémantique,
    - un corpus BM25 pour la recherche lexicale basée sur les mots-clés.
    """
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Encodage des documents avec FAISS**")
        st.code(
            """
            # scripts/build_hybrid_index.py
            model = SentenceTransformer("intfloat/multilingual-e5-base")
            embs = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
            index = faiss.IndexFlatIP(embs.shape[1])
            index.add(embs)
            faiss.write_index(index, "./indices/dense.index")
            """,
            language="python",
        )
        st.caption("Chaque document est transformé en vecteur dense et ajouté à l’index FAISS (similarité cosinus).")
    with col2:
        st.markdown("**Construction du corpus BM25**")
        st.code(
            """
            with open("./indices/bm25_corpus.txt", "w", encoding="utf-8") as f:
                for r in records:
                    f.write(" ".join(tokenize(r["text"])) + "\\n")
            """,
            language="python",
        )
        st.caption("Les textes sont tokenisés pour permettre une recherche lexicale robuste.")

    st.markdown("**Fusion FAISS + BM25 lors du Retrieval (api/retriever.py)**")
    st.code(
        """
        combined = {}
        for i, cid in enumerate(dense_ids):
            combined[cid] = combined.get(cid, 0) + (10 - i)
        for i, cid in enumerate(bm25_ids):
            combined[cid] = combined.get(cid, 0) + (10 - i)
        candidate_ids = sorted(combined, key=combined.get, reverse=True)[:30]
        """,
        language="python",
    )

    st.markdown("**Comportement réel dans le projet :**")
    st.write(
        """
        - Le Retriever recherche d’abord dans les deux espaces (FAISS et BM25).  
        - Il fusionne les résultats avec un score pondéré pour prioriser les passages communs.  
        - Ces passages candidats sont ensuite envoyés au **CrossEncoder** pour re-ranking.  
        """
    )

    with st.expander("Pourquoi FAISS + BM25 dans SynapseDesk"):
        st.write(
            """
            - **BM25** capture les mots exacts, acronymes et noms de processus internes.  
            - **FAISS** comprend les formulations variées ou traduites.  
            - Leur **fusion** assure robustesse et couverture complète, essentielle en environnement hétérogène.  
            """
        )

# --------------------------------

# 4. Re-ranking

# --------------------------------

with tabs[3]:
    st.subheader("Étape de Re-ranking avec CrossEncoder")
    st.markdown(
    """
    Une fois les candidats récupérés par FAISS et BM25, il est nécessaire de **réévaluer leur pertinence**
    en tenant compte de la question utilisateur.
    Cette étape est cruciale pour éviter que le LLM lise des passages approximatifs ou non prioritaires.
    Elle repose sur un modèle **CrossEncoder**, qui prédit un score de similarité *question ↔ passage*.
    """
    )

    st.markdown("**Principe du CrossEncoder**")
    st.write(
        """
        - Le modèle prend **chaque paire (question, passage)** comme entrée.  
        - Il calcule un **score de correspondance** basé sur le contexte combiné, contrairement aux embeddings
        où les textes sont encodés séparément.  
        - Plus le score est élevé, plus le passage est jugé pertinent.  
        - Les meilleurs passages (top-k) sont ensuite transmis à l’étape de génération du LLM.
        """
    )

    st.code(
        """
        # api/retriever.py
        from sentence_transformers import CrossEncoder

        cross = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        pairs = [(query, records[i]["text"]) for i in candidate_ids]
        rerank_scores = cross.predict(pairs)

        scored = []
        for i, cid in enumerate(candidate_ids):
            scored.append({
                "id": cid,
                "score": float(rerank_scores[i]),
                "text": records[cid]["text"],
                "path": records[cid]["path"],
            })

        hits = sorted(scored, key=lambda x: x["score"], reverse=True)[:8]
        """,
        language="python",
    )

    st.markdown("**Pourquoi cette étape est indispensable dans SynapseDesk**")
    st.write(
        """
        - 🔍 Le CrossEncoder permet d’éliminer les faux positifs issus de FAISS ou BM25.  
        - ⚙️ Il prend en compte la sémantique complète de la question et du passage ensemble.  
        - 💬 Il améliore la cohérence des réponses en orientant le LLM vers les sources vraiment pertinentes.  
        - ⏱️ Même s’il est plus coûteux, il reste viable localement grâce au modèle compact `MiniLM-L-6-v2`.  
        """
    )

    with st.expander("Notes techniques et optimisation"):
        st.write(
            """
            - On limite le **nombre de passages rerankés (ex : 30 → 8)** pour réduire la latence.  
            - Le modèle CrossEncoder est chargé une seule fois lors du démarrage de l’API FastAPI.  
            - Des variantes multilingues peuvent être utilisées si le corpus contient des textes anglais/français.  
            - Pour des environnements GPU, l’utilisation de `device_map='auto'` accélère fortement le scoring.  
            """
        )


# --------------------------------

# 5. Synthèse LLM

# --------------------------------

with tabs[4]:
    st.subheader("Synthèse de la réponse avec le LLM (Mistral via Ollama)")
    st.markdown(
    """
    Après la sélection et le classement des passages les plus pertinents,
    la dernière étape consiste à **construire un prompt clair et structuré**
    pour le modèle de langage, afin qu’il génère une réponse **fiable, concise et sourcée**.
    """
    )

    st.markdown("**🧩 Construction du prompt**")
    st.code(
        """
        ctx_text = "\\n\\n---\\n\\n".join([f"Source ({c['path']}):\\n{c['text']}" for c in contexts])

        prompt = f\"\"\"
        Tu es un assistant d'entreprise spécialisé dans le support aux équipes techniques et fonctionnelles.
        Utilise les informations suivantes pour répondre à la question :

        Question : {q}

        Contexte :
        {ctx_text}

        Structure ta réponse avec :
        - Résumé
        - Analyse
        - Recommandations concrètes
        - Sources (liste)
        \"\"\"
        """,
        language="python",
    )
    st.caption("Chaque passage du contexte est concaténé pour créer un prompt complet et traçable.")

    # ---- Ollama ----
    st.subheader("🚀 Exécution locale via Ollama")
    st.write(
        """
        **Ollama** est une plateforme open source qui permet d’exécuter des modèles de langage (LLM) 
        **en local**, sans dépendance cloud.  
        Il gère le téléchargement, la quantification (compression GPU/CPU), 
        et l’exécution efficace des modèles comme **Mistral**, **Llama 3**, ou **Gemma**.
        """
    )

    st.markdown("Appel Ollama via `/api/generate` (Mistral local)")
    st.code(
        """
        # api/llm_manager.py
        OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
        OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }

        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        answer = r.json().get("response", "")
        """,
        language="python",
    )

    st.markdown("**Comment ça marche**")
    st.write(
        """
        1. Le backend FastAPI envoie le prompt à l’API d’Ollama (`/api/chat`).  
        2. Ollama charge le modèle spécifié (par défaut `mistral:latest`).  
        3. Le modèle génère le texte réponse localement, sans connexion externe.  
        4. La réponse est renvoyée à Streamlit pour affichage, avec les citations associées.  
        """
    )

    # ---- Pourquoi Mistral ----
    st.subheader("🧠 Pourquoi Mistral ?")
    st.write(
        """
        **Mistral 7B** (version *Instruct*) a été choisi pour son équilibre entre **performance, taille et localité** :
        - Modèle compact (7 milliards de paramètres) performant sur CPU/GPU modestes.  
        - Excellente compréhension du français et du vocabulaire technique (data, IT, RH…).  
        - Ouvert, rapide et bien supporté par Ollama.  
        - Très faible coût matériel comparé à GPT ou Claude.  
        """
    )

    st.markdown("**Alternatives possibles**")
    st.write(
        """
        - 🦙 **Llama 3 (8B / 13B)** → plus précis, mais plus lourd.  
        - 🧮 **Phi-3-mini (Microsoft)** → très léger, idéal CPU.  
        - 🔬 **Gemma 2 (Google)** → excellent en raisonnement, mais encore en test sur Ollama.  
        - 🌍 **Mixtral 8x7B** → version Mixture-of-Experts du modèle Mistral, plus puissante mais nécessite GPU ≥ 12 Go.  
        """
    )

    with st.expander("Détails techniques de l'intégration Mistral/Ollama"):
        st.write(
            """
            - L’appel à Ollama se fait via HTTP local (`localhost:11434`).  
            - Le modèle reste en mémoire (grâce à `OLLAMA_KEEP_ALIVE`) pour des réponses instantanées.  
            - La température et le `top_p` peuvent être ajustés dans `llm_manager.py` pour moduler la créativité.  
            - En cas d’erreur ou de service Ollama inactif, un **fallback automatique** vers HuggingFace peut être ajouté.  
            """
        )


# --------------------------------

# 6. Logique d’adaptation

# --------------------------------

with tabs[5]:
    st.subheader("Logique d’adaptation : quand activer ou non le RAG")
    st.markdown(
    """
    Dans **SynapseDesk**, le système ne se contente pas d’injecter les passages trouvés à chaque question.
    Il **évalue dynamiquement la pertinence moyenne** des documents rerankés, afin de choisir entre deux modes :

    ```
        - 🧩 **Mode RAG** : les sources internes sont jugées fiables et intégrées dans la réponse.  
        - 💬 **Mode Chat libre** : les résultats sont trop faibles, le LLM répond seul sans contexte.
    """
    )

    st.markdown("**🔎 Principe de détection automatique**")
    st.write(
        """
        Le système vérifie le **score maximal** parmi les passages rerankés.  
        Si ce score est trop faible (inférieur à `0.01`) et que la requête semble bien une question,
        le modèle considère que le contexte RAG serait peu utile et bascule en **chat libre**.
        """
    )

    st.code(
        """
        # api/main.py
        max_score = max(h["score"] for h in hits)

        if max_score < 0.01 and "?" in q:
            answer = generate_with_ollama(f"Réponds clairement à : {q}", max_tokens=512)
            return {"answer": answer, "citations": []}
        else:
            # RAG normal avec les passages les plus pertinents
        """,
        language="python",
    )

    st.markdown("**🎛 Paramétrage possible**")
    st.write(
        """
        - Le **seuil de déclenchement (0.01)** est défini dans `api/main.py`.  
        - Un seuil plus haut rend la détection plus stricte (le RAG s’active moins souvent).  
        - La condition `"?" in q` permet d’éviter d’activer le mode libre sur des entrées non interrogatives.  
        - Cette approche garantit que le LLM ne réponde librement **que lorsqu’aucune source interne n’est pertinente**.
        """
    )

    st.markdown("**Pourquoi cette logique est essentielle**")
    st.write(
        """
        - ✅ Évite les réponses polluées par des logs ou documents hors sujet.  
        - 🧠 Réduit le risque d’hallucination contextuelle.  
        - 🔍 Améliore la lisibilité des résultats pour les utilisateurs non techniques.  
        - ⚖️ Offre un équilibre entre précision (RAG) et flexibilité (chat libre).  
        """
    )

    with st.expander("Schéma conceptuel de la bascule automatique"):
            st.graphviz_chart(
                """
                digraph Adaptation {
                rankdir=LR;
                node [shape=box, style=filled, color="#1E1E2E", fontcolor="white", fillcolor="#2A2A3B"];
                edge [color="#8AA1B1"];

                Q [label="Question utilisateur"];
                R [label="Retrieval + Re-ranking"];
                S [label="Évaluation du score maximal"];
                RAG [label="Mode RAG actif (sources internes)"];
                CHAT [label="Mode Chat libre (sans contexte)"];

                Q -> R -> S;
                S -> RAG [label="max_score ≥ 0.01", color="#10b981"];
                S -> CHAT [label="max_score < 0.01", color="#ef4444"];
                }
                """
            )

    with st.expander("Exemples pratiques"):
        st.write(
            """
            - 🧠 *Question technique claire* → "Pourquoi mon job Spark met 10 minutes à s’exécuter ?"  
            → score élevé, activation du RAG (réponse basée sur les logs internes).  
            - 💬 *Question vague ou RH* → "Comment va l’équipe ce mois-ci ?"  
            → score faible, passage en mode chat libre avec réponse générique.  
            """
        )


# --------------------------------

# 7. Tests et Validation

# --------------------------------

with tabs[6]:
    st.subheader("Tests et validation du système RAG")
    st.markdown(
    """
    Une fois le pipeline complet en place, il est essentiel de **valider la cohérence, la précision et la robustesse**
    du modèle RAG. Les tests garantissent que le système comprend bien les questions,
    sélectionne des sources pertinentes et produit des réponses fiables.
    """
    )

    st.markdown("**🎯 Types de tests menés dans SynapseDesk**")
    st.write(
        """
        - **Questions de référence techniques** : validation sur des jobs Spark, erreurs OOM, ou scripts internes.  
        - **Cas non techniques** : documents RH, politiques internes, fiches métiers.  
        - **Cas limites** : acronymes, abréviations, fautes d’orthographe ou expressions multilingues.  
        - **Mesures quantitatives** :  
        - Temps de réponse API (FastAPI + Ollama).  
        - Ratio d’activation du mode RAG vs. chat libre.  
        - Taux de citations exactes des sources (path + snippet).  
        """
    )

    st.subheader("🧪 Exemple de test rapide via l’API FastAPI")
    st.code(
        r"""
    ```

    curl -X POST [http://127.0.0.1:8000/query](http://127.0.0.1:8000/query) -H "Content-Type: application/json" ^
    -d "{"query": "Pourquoi mon job bronze_to_silver est lent ?"}"
    """,
    language="bash",
    )

    st.markdown("**Interprétation du résultat**")
    st.write(
        """
        - Si le message `ℹ️ Aucune source interne trouvée` apparaît → le système a basculé en **chat libre**.  
        - Si plusieurs sources (`data\\...json`) sont listées → le **RAG est actif**, et la réponse est sourcée.  
        - En mode démo, les logs FastAPI affichent :  
        `"[Retriever] Top N résultats après rerank."`, confirmant le bon fonctionnement du moteur hybride.  
        """
    )

    with st.expander("Bonnes pratiques de validation continue"):
        st.write(
            """
            - Maintenir un **jeu de tests récurrents** (fichier JSON de Q/A attendues).  
            - Surveiller l’évolution du **score moyen** après chaque mise à jour du corpus.  
            - Évaluer régulièrement la **pertinence perçue** via des retours utilisateurs internes.  
            - Intégrer ces tests dans un workflow CI (GitHub Actions ou Makefile dédié).  
            """
        )

    # --------------------------------

    # 8. Configuration et Déploiement

    # --------------------------------

    with tabs[7]:
        st.subheader("🧩 Fichier de configuration : settings.yaml")
        st.markdown(
        """
        Le fichier `configs/settings.yaml` centralise les **chemins**, **modèles** et **paramètres de seuil** utilisés par le projet.
        Il permet d’ajuster le comportement global sans modifier le code Python.
        """
        )
        st.code(settings_text, language="yaml")
        st.caption("Les paramètres contrôlent notamment : le chemin du corpus, le modèle d’embedding, et les seuils d’activation du RAG.")

        st.subheader("⚙️ Commandes Makefile principales")
        st.markdown(
            """
            Les principales étapes du pipeline sont automatisées via le **Makefile**.
            Cela garantit un déploiement rapide et cohérent, que ce soit en local ou sur serveur.
            """
        )
        st.code(
            """
            make setup           # Création du venv + installation requirements
            make generate-data   # Génère un petit jeu de données de test
            make ingest          # Produit api/output/corpus.jsonl (via ingest_data.py)
            make build-index     # Construit l'index FAISS + BM25 à partir du corpus
            make api             # Lance le backend FastAPI (http://127.0.0.1:8000)
            make streamlit       # Lance l’interface Streamlit
            """,
            language="bash",
        )

        st.subheader("🚀 Déploiement et bonnes pratiques")
        st.write(
            """
            - **Versionnement** : conserver une copie du dossier `indices/` et du corpus `api/output/corpus.jsonl` pour rejouer les mêmes résultats.  
            - **Performance GPU** : ajuster `OLLAMA_NUM_PARALLEL` (sessions concurrentes) et `OLLAMA_KEEP_ALIVE` pour réduire la latence.  
            - **Logs d’usage** : consigner les requêtes, temps de réponse et passages cités pour l’audit interne.  
            - **Sécurité** : filtrer les données sensibles (PII) avant ingestion, et limiter les accès API à l’intranet.  
            - **Extensibilité** : prévoir un dossier `api/plugins/` pour des retrievers spécialisés (RH, incidents, tickets…).  
            """
        )

        with st.expander("📦 Exemple de déploiement local complet"):
            st.markdown(
                """
                ```bash
                git clone https://github.com/TifraYanis/synapsedesk
                cd synapsedesk
                make setup
                make ingest
                make build-index
                make api
                make streamlit
                ```
                → Accès local à l’API : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
                → Interface Streamlit : [http://localhost:8501](http://localhost:8501)
                """
            )

# --------------------------------

# 9. Schéma global

# --------------------------------

with tabs[8]:
    st.subheader("🗺️ Schéma global du pipeline SynapseDesk")
    st.markdown(
    """
    Le diagramme ci-dessous illustre le **flux complet de traitement** des requêtes dans SynapseDesk :
    de la collecte de données internes jusqu’à la réponse structurée du modèle Mistral.
    """
    )

    st.graphviz_chart(
        """
        digraph G {
        rankdir=LR;
        node [shape=box, style=filled, color="#1E1E2E", fontcolor="white", fillcolor="#2A2A3B"];
        edge [color="#8AA1B1"];

        A [label="Sources internes (md, txt, html, docx, logs, code)"];
        B [label="Ingestion & Normalisation (ingest_data.py)"];
        C [label="Embeddings (E5 - dense)"];
        D [label="Index FAISS"];
        E [label="Index BM25"];
        Q [label="Question utilisateur"];
        R [label="Fusion candidats (dense + BM25)"];
        X [label="Re-ranking CrossEncoder"];
        CTX [label="Top-k context généré"];
        LLM [label="LLM local (Ollama + Mistral)"];
        OUT [label="Réponse structurée + Citations"];
        F [label="Fallback chat libre (si max_score < 0.01)"];

        A -> B -> C -> D;
        B -> E;
        Q -> R;
        D -> R;
        E -> R;
        R -> X -> CTX -> LLM -> OUT;
        X -> F [style=dashed, label="max_score faible (< 0.01)"];
        }
        """
    )


    st.markdown(
            """
            ### 🔄 Lecture du pipeline
            1. **Ingestion & Normalisation** : tous les fichiers internes (`api/data/`) sont lus et convertis en texte brut via `ingest_data.py`.  
            → Les formats pris en charge incluent `.md`, `.txt`, `.html`, `.docx`, `.json`, et certains scripts `.py`.  
            2. **Indexation hybride** :  
            - **FAISS** encode chaque texte avec des **embeddings sémantiques** (`intfloat/multilingual-e5-base`).  
            - **BM25** conserve une **indexation lexicale** (mots-clés exacts, acronymes, noms de jobs, etc.).  
            3. **Retrieval & Fusion** : les résultats FAISS et BM25 sont combinés avec pondération pour produire une liste unifiée de passages candidats.  
            4. **Re-ranking** : un modèle CrossEncoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) reclasse les passages selon leur pertinence réelle vis-à-vis de la question.  
            5. **Synthèse** : le modèle **Mistral 7B** (exécuté localement via **Ollama**) rédige une réponse structurée : *Résumé, Analyse, Recommandations, Sources*.  
            6. **Fallback automatique** : si le **score maximal** des passages est inférieur à `0.01`, le système considère qu’aucune source interne n’est pertinente et bascule en **chat libre**.  
            """
        )

    st.info(
        "💡 Utilisez l’onglet **Tests** pour observer le comportement du pipeline et voir quand le RAG s’active ou non.",
        icon="🔍"
    )

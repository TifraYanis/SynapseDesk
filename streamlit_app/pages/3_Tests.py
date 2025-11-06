import streamlit as st
import requests
import os
import time
from streamlit_extras.colored_header import colored_header

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Tests RAG", page_icon="🧠", layout="wide")

# --- En-tête ---
colored_header(
    label="🧪 Scénarios de test – RAG Ops Copilot",
    description="Explorez différents profils et types de questions pour visualiser comment le moteur RAG combine les données internes et les connaissances générales.",
    color_name="violet-70"
)

# --- Définition des scénarios enrichis ---
scenarios = {
    "👷‍♂️ Data Engineer": [
        "Pourquoi mon job bronze_to_silver est lent ?",
        "Comment corriger un OOM sur un job PySpark ?",
        "Quelle est la bonne pratique pour gérer les joins volumineux ?",
    ],
    "🧑‍💼 Product Owner": [
        "Quels sont les indicateurs clés du projet Data Platform ?",
        "Comment suivre les performances des jobs Spark ?",
    ],
    "👩‍💻 RH / Manager": [
        "Quelle est la procédure d'onboarding d’un nouveau collaborateur data ?",
        "Comment contacter l’équipe Data Platform ?",
    ],
    "📊 Conseiller Métier": [
        "Comment analyser les logs d’un job échoué ?",
        "Que faire en cas de ticket incident récurrent ?",
    ],
    "🌍 Général / LLM pur": [
        "C’est quoi Spark et à quoi ça sert ?",
        "Quelle est la capitale du Japon ?"
    ]
}

# --- Interface ---
st.write("### Choisissez un profil et testez une question :")

profil = st.selectbox("Sélectionnez un profil :", list(scenarios.keys()))
questions = scenarios[profil]
selected_question = st.selectbox("Choisissez une question :", questions)

if st.button("🚀 Lancer le test", use_container_width=True):
    t0 = time.time()
    try:
        r = requests.post(f"{API_URL}/query", json={"query": selected_question}, timeout=300)
        latency = time.time() - t0
        if not r.ok:
            st.error(f"Erreur API ({r.status_code}): {r.text}")
        else:
            data = r.json()
            st.success(f"Réponse reçue en {latency:.2f} s ✅")
            st.markdown(f"### 🧠 Question : *{selected_question}*")
            st.markdown("---")

            st.markdown("#### 💬 Réponse :")
            st.markdown(data.get("answer", "_Aucune réponse_"))

            if data.get("citations"):
                st.markdown("#### 📚 Sources RAG :")
                for c in data["citations"]:
                    with st.expander(f"📄 {c['source']} (score {round(c['score'],3)})"):
                        st.code(c.get("snippet", ""), language="text")
            else:
                st.info("ℹ️ Aucune source interne trouvée, réponse purement LLM.")
    except Exception as e:
        st.error(f"Erreur de communication avec l’API : {e}")

st.markdown("---")
st.markdown("""
### 🧩 Notes :
- Les questions "Data Engineer" / "PO" / "RH" / "Conseiller" activent le **RAG** (recherche sur les fichiers internes).
- Les questions "Général / LLM pur" sont là pour tester le **fallback vers Ollama seul**.
- Vous pouvez observer les temps de réponse et la présence (ou non) de citations internes.
""")

import streamlit as st
from pathlib import Path

# ------------------------------
# CONFIGURATION DE LA PAGE
# ------------------------------
st.set_page_config(
    page_title="SynapseDesk",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------
# STYLES PERSONNALISÉS
# ------------------------------
css_path = Path(__file__).parent / "assets" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ------------------------------
# HERO SECTION
# ------------------------------
st.markdown(
    """
    <div style="text-align:center; padding:40px 0;">
      <h1 style="font-size:2.8em; color:#00BFA6; margin-bottom:0;">SynapseDesk</h1>
      <p style="font-size:1.2em; color:rgba(255,255,255,0.85); margin-top:0.5em;">
        L’assistant cognitif qui connecte la connaissance interne à la puissance du langage.
      </p>
      <p style="font-size:1em; color:rgba(255,255,255,0.6);">
        Développé par <b>Yanis Tifra</b> | Data Engineer & AI Enthusiast
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------------------
# PRESENTATION DU PROJET
# ------------------------------
st.markdown(
    """
    ### 🧭 Pourquoi ce projet ?

    Les entreprises disposent de milliers de documents internes, mais peu de moyens
    pour interroger cette base de connaissances efficacement.  
    **SynapseDesk** est un *RAG local (Retrieval-Augmented Generation)* qui combine :
    - 🔍 Indexation hybride (BM25 + embeddings FAISS)
    - 🧩 Re-ranking intelligent (CrossEncoder)
    - 🤖 Génération contextuelle (Ollama + Mistral)

    Il agit comme un **copilote interne** pour les équipes Data, RH, métiers et support.
    """
)

st.divider()

# ------------------------------
# COMMENT ÇA MARCHE
# ------------------------------
st.markdown(
    """
    ### ⚙️ Comment ça marche ?

    1. **Ingestion** des fichiers internes (PDF, DOCX, MD, logs, tickets, etc.)  
    2. **Indexation hybride** pour recherche rapide et pertinente  
    3. **Réponse augmentée** : génération cohérente, sourcée et traçable  
    4. **Interface Streamlit** : test, exploration et validation du RAG

    """
)

st.info(
    """
    **Astuce :** plus vos données internes sont riches et bien structurées,
    plus SynapseDesk sera précis dans ses réponses.
    """,
    icon="💡"
)

st.divider()

# ------------------------------
# LIENS PERSONNELS
# ------------------------------
st.markdown(
    """
    ### 🔗 Liens & Contacts

    - 📂 [GitHub – TifraYanis](https://github.com/TifraYanis)
    - 💼 [LinkedIn – Yanis Tifra](https://www.linkedin.com/in/yanis-tifra/)
    - ✉️ ytifra@gmail.com
    """,
    unsafe_allow_html=True,
)

st.success("👈 Sélectionnez une page dans la barre latérale pour explorer le projet.", icon="🧭")

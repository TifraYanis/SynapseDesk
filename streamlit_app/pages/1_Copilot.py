import streamlit as st
import requests
import time
import json
import os

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Copilot", page_icon="💬", layout="wide")
st.markdown("<h2 class='page-title'>💬 Copilot</h2>", unsafe_allow_html=True)

# Etat de session: conversations
if "conversations" not in st.session_state:
    st.session_state.conversations = {}  # id -> list of messages
if "current_conv" not in st.session_state:
    st.session_state.current_conv = "Conversation 1"
    st.session_state.conversations[st.session_state.current_conv] = []

def new_conversation():
    idx = len(st.session_state.conversations) + 1
    name = f"Conversation {idx}"
    st.session_state.conversations[name] = []
    st.session_state.current_conv = name

with st.sidebar:
    st.header("Conversations")
    if st.button("➕ Nouvelle conversation", use_container_width=True):
        new_conversation()
    conv_names = list(st.session_state.conversations.keys())
    st.session_state.current_conv = st.radio("Sélection", conv_names, index=conv_names.index(st.session_state.current_conv))
    st.caption("Les conversations sont conservées tant que la session reste ouverte.")

def ask_backend(question: str) -> dict:
    t0 = time.time()
    r = requests.post(f"{API_URL}/query", json={"query": question}, timeout=300)
    r.raise_for_status()
    data = r.json()
    data["_latency"] = time.time() - t0
    return data

# Zone de chat
msgs = st.session_state.conversations[st.session_state.current_conv]

for m in msgs:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])
        if m.get("citations"):
            with st.expander("Citations"):
                for c in m["citations"]:
                    st.markdown(f"- **{c['source']}** — score {round(c['score'],3)}")
                    if "snippet" in c:
                        st.code(c["snippet"])

question = st.chat_input("Posez une question")
if question:
    # affiche la question
    msgs.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # spinner + status
    with st.chat_message("assistant"):
        with st.spinner("Mistral réfléchit..."):
            try:
                data = ask_backend(question)
                answer = data.get("answer", "").strip()
                citations = data.get("citations", [])
                latency = data.get("_latency", 0.0)

                # rendu structuré
                st.markdown(f"<div class='latency'>Réponse générée en {latency:.2f}s</div>", unsafe_allow_html=True)
                st.markdown(answer)

                if citations:
                    st.markdown("**Citations**")
                    for c in citations:
                        with st.expander(f"{c['source']} — score {round(c['score'],3)}"):
                            st.code(c.get("snippet",""))

                msgs.append({"role": "assistant", "content": answer, "citations": citations})
            except Exception as e:
                st.error(f"Erreur API: {e}")

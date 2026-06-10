import streamlit as st
import os
import zipfile
import shutil

from query import ask_question

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Code Chatter",
    layout="wide"
)

# ---------------- ENSURE DATA FOLDER EXISTS ----------------

DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- HEADER ----------------

st.title("💻 Code Chatter")
st.markdown("### Multi-Repo Code Analysis using AI")

# ---------------- SIDEBAR ----------------

st.sidebar.title("ℹ️ About")
st.sidebar.info(
    "Multi-repo RAG system for codebase understanding."
)

# ---------------- REPO UPLOAD ----------------

st.sidebar.markdown("## 🚀 Demo Mode")

st.sidebar.info(
    """
    Public deployment uses pre-indexed repositories.

    Repository ingestion is available
    in the local development version.
    """
)

# ---------------- LOAD REPOSITORIES ----------------

repos = [
    r
    for r in os.listdir(DATA_DIR)
    if os.path.isdir(os.path.join(DATA_DIR, r))
]

# ---------------- NO REPO CASE ----------------

if not repos:
    st.warning(
        "No repositories found locally."
    )

    repos = [
        "AI-driven-health-monitoring-system-using-ayurveda"
    ]

# ---------------- SELECT REPO ----------------

selected_repo = st.selectbox(
    "📂 Select Repository",
    repos
)

# ---------------- CHAT HISTORY ----------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- QUESTION INPUT ----------------

query = st.text_input(
    "🔍 Ask your question:"
)

# ---------------- ASK BUTTON ----------------

if st.button("Ask"):

    if query.strip():

        with st.spinner("🧠 Analyzing repository..."):

            result = ask_question(
                query,
                selected_repo,
                st.session_state.chat_history
            )

        st.session_state.chat_history.append(
            (
                query,
                result
            )
        )

# ---------------- DISPLAY CHAT ----------------

st.markdown("## 💬 Conversation")

for q, res in st.session_state.chat_history:

    st.markdown(f"### 🧑 {q}")

    if res["files"]:

        st.markdown("#### 📂 Relevant Files")

        for file in res["files"]:
            st.code(file)

    st.markdown("#### 🧠 Answer")

    st.write(res["answer"])
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

st.sidebar.markdown("## 📤 Upload Repository")

uploaded_file = st.sidebar.file_uploader(
    "Upload ZIP repo",
    type=["zip"]
)

if uploaded_file is not None:

    repo_name = uploaded_file.name.replace(".zip", "")

    st.sidebar.success(f"📦 Selected: {repo_name}")

    if st.sidebar.button("🚀 Ingest Repository"):

        extract_path = os.path.join(DATA_DIR, repo_name)

        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)

        zip_path = os.path.join(
            DATA_DIR,
            uploaded_file.name
        )

        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        os.remove(zip_path)

        from ingest import ingest

        with st.spinner("🔄 Ingesting repository..."):

            ingest(
                extract_path,
                repo_name
            )

        st.sidebar.success(
            f"✅ {repo_name} ingested successfully!"
        )

        st.rerun()

# ---------------- LOAD REPOSITORIES ----------------

repos = [
    r
    for r in os.listdir(DATA_DIR)
    if os.path.isdir(os.path.join(DATA_DIR, r))
]

# ---------------- NO REPO CASE ----------------

if not repos:

    st.info(
        "📤 Upload a repository ZIP file from the sidebar to begin."
    )

    st.stop()

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
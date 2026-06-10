import streamlit as st
import os
import zipfile
import shutil
from query import ask_question

st.set_page_config(page_title="Code Chatter", layout="wide")

st.title("💻 Code Chatter")
st.markdown("### Multi-Repo Code Analysis using AI")

# ---------------- SIDEBAR ----------------
st.sidebar.title("ℹ️ About")
st.sidebar.info("Multi-repo RAG system for codebase understanding.")

# Upload section
st.sidebar.markdown("## 📤 Upload Repository")
uploaded_file = st.sidebar.file_uploader(
    "Upload ZIP repo",
    type=["zip"]
)

if uploaded_file is not None:

    repo_name = uploaded_file.name.replace(".zip", "")

    st.sidebar.success(f"📦 Selected: {repo_name}")

    if st.sidebar.button("🚀 Ingest Repository"):

        extract_path = f"../data/{repo_name}"

        if os.path.exists(extract_path):
            st.sidebar.warning(
                f"{repo_name} already exists. Overwriting..."
            )
            shutil.rmtree(extract_path)

        zip_path = f"../data/{uploaded_file.name}"

        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        os.remove(zip_path)

        from ingest import ingest

        with st.spinner("🔄 Ingesting repository..."):
            ingest(extract_path, repo_name)

        st.sidebar.success(
            f"✅ {repo_name} ingested successfully!"
        )

        st.rerun()

# ---------------- MAIN UI ----------------

repo_path = "../data"
repos = [r for r in os.listdir(repo_path) if os.path.isdir(os.path.join(repo_path, r))]

selected_repo = st.selectbox("📂 Select Repository", repos)

query = st.text_input("🔍 Ask your question:")

# Chat memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Ask button
if st.button("Ask"):
    if query:
        with st.spinner("Analyzing..."):
            result = ask_question(query, selected_repo, st.session_state.chat_history)

        st.session_state.chat_history.append((query, result))

# Display chat
st.markdown("## 💬 Conversation")

for q, res in st.session_state.chat_history:
    st.markdown(f"### 🧑 {q}")

    st.markdown("#### 📂 Relevant Files")
    for f in res["files"]:
        st.code(f)

    st.markdown("#### 🧠 Answer")
    st.write(res["answer"])  
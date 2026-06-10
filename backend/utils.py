import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings


# ✅ Load files
def load_code_files(repo_path):
    code_files = []

    print("🔍 Scanning:", repo_path)

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(
    (
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".cs",
        ".go",
        ".rs",
        ".md",
        ".txt"
    )
):
                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    code_files.append({
                        "path": path,
                        "content": content
                    })

                except Exception as e:
                    print("Error:", path, e)

    print("✅ Files loaded:", len(code_files))
    return code_files


# ✅ Split code
def split_code(files):
    splitter = RecursiveCharacterTextSplitter.from_language(
        language="python",
        chunk_size=400,
        chunk_overlap=50
    )

    docs = []

    for file in files:
        chunks = splitter.split_text(file["content"])

        for chunk in chunks:
            docs.append({
                "text": chunk,
                "path": file["path"]
            })

    return docs


# ✅ Embedding model
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
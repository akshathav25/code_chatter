import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


def load_code_files(repo_path):
    files_data = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith((".py", ".js", ".ts")):
                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    files_data.append({
                        "path": path,
                        "content": content
                    })

                except:
                    pass

    return files_data


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


def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
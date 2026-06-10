import os
import weaviate
from config import WEAVIATE_URL
from utils import (
    load_code_files,
    split_code,
    get_embedding_model
)

# Connect Weaviate
client = weaviate.Client(WEAVIATE_URL)

# Embedding model
embedding_model = get_embedding_model()


# --------------------------------------------------
# Create Schema
# --------------------------------------------------
def create_schema():

    existing_classes = [
        c["class"]
        for c in client.schema.get()["classes"]
    ]

    if "CodeChunk" in existing_classes:
        print("✅ Schema already exists")
        return

    schema = {
        "class": "CodeChunk",
        "vectorizer": "none",
        "properties": [
            {
                "name": "text",
                "dataType": ["text"]
            },
            {
                "name": "path",
                "dataType": ["string"]
            },
            {
                "name": "repo",
                "dataType": ["string"]
            }
        ]
    }

    client.schema.create_class(schema)

    print("✅ Schema created")


# --------------------------------------------------
# Check if repo already ingested
# --------------------------------------------------
def repo_already_exists(repo_name):

    result = (
        client.query
        .get("CodeChunk", ["repo"])
        .with_where({
            "path": ["repo"],
            "operator": "Equal",
            "valueString": repo_name
        })
        .with_limit(1)
        .do()
    )

    try:
        return len(result["data"]["Get"]["CodeChunk"]) > 0
    except:
        return False


# --------------------------------------------------
# Ingest Single Repo
# --------------------------------------------------
def ingest(repo_path, repo_name):

    print(f"\n🚀 Ingesting: {repo_name}")

    files = load_code_files(repo_path)

    print(f"📁 Files loaded: {len(files)}")

    if len(files) == 0:
        print("❌ No code files found")
        return

    docs = split_code(files)

    print(f"📦 Chunks created: {len(docs)}")

    for i, doc in enumerate(docs):

        vector = embedding_model.embed_query(
            doc["text"]
        )

        client.data_object.create(
            {
                "text": doc["text"],
                "path": doc["path"],
                "repo": repo_name
            },
            "CodeChunk",
            vector=vector
        )

        if i % 100 == 0:
            print(
                f"Inserted {i}/{len(docs)} chunks"
            )

    print(f"✅ Finished: {repo_name}")


# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":

    create_schema()

    BASE_PATH = "../data"

    repos = os.listdir(BASE_PATH)

    for repo in repos:

        repo_path = os.path.join(
            BASE_PATH,
            repo
        )

        if not os.path.isdir(repo_path):
            continue

        if repo_already_exists(repo):
            print(
                f"⏭️ Skipping {repo} "
                "(already ingested)"
            )
            continue

        ingest(repo_path, repo)

    print("\n🎉 ALL REPOSITORIES INGESTED")
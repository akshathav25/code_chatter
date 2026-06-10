import os
import weaviate
from weaviate.auth import AuthApiKey
from config import WEAVIATE_URL, WEAVIATE_API_KEY
from utils import load_code_files, split_code, get_embedding_model

client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=AuthApiKey(WEAVIATE_API_KEY)
)
embedding_model = get_embedding_model()


def create_schema():
    if client.schema.exists("CodeChunk"):
        print("Schema exists")
        return

    schema = {
        "class": "CodeChunk",
        "vectorizer": "none",
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "path", "dataType": ["string"]},
            {"name": "repo", "dataType": ["string"]}
        ]
    }

    client.schema.create_class(schema)
    print("Schema created")


def ingest(repo_path, repo_name):
    files = load_code_files(repo_path)

    docs = split_code(files)
    print(f"{repo_name}: {len(docs)} chunks")

    for i, doc in enumerate(docs):
        vector = embedding_model.embed_query(doc["text"])

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
            print(f"{repo_name}: {i}/{len(docs)}")

def repo_already_exists(repo_name):
    result = client.query.get("CodeChunk", ["repo"]) \
        .with_where({
            "path": ["repo"],
            "operator": "Equal",
            "valueString": repo_name
        }) \
        .with_limit(1) \
        .do()

    return len(result["data"]["Get"]["CodeChunk"]) > 0

    print(f"✅ Ingestion complete for {repo_name}")


if __name__ == "__main__":
    create_schema()

    BASE_PATH = "../data"

    for repo in os.listdir(BASE_PATH):
        repo_path = os.path.join(BASE_PATH, repo)

        if os.path.isdir(repo_path):

            if repo_already_exists(repo):
                print(f"⏭️ Skipping {repo} (already ingested)")
                continue

            print(f"\n🚀 Ingesting {repo}")
            ingest(repo_path, repo)
import weaviate
from weaviate.auth import AuthApiKey
from config import WEAVIATE_URL, WEAVIATE_API_KEY, GROQ_API_KEY
from langchain_groq import ChatGroq
from utils import get_embedding_model

def get_client():
    return weaviate.Client(
        url=WEAVIATE_URL,
        auth_client_secret=AuthApiKey(WEAVIATE_API_KEY)
    )

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant"
)

embedding_model = get_embedding_model()

def search_code(query, repo_name):
    client = get_client()
    
    query_vector = embedding_model.embed_query(query)

    result = client.query.get("CodeChunk", ["text", "path"]) \
        .with_where({
            "path": ["repo"],
            "operator": "Equal",
            "valueString": repo_name
        }) \
        .with_near_vector({"vector": query_vector}) \
        .with_limit(5) \
        .do()

    return result["data"]["Get"]["CodeChunk"]


def ask_question(query, repo_name, chat_history):
    results = search_code(query, repo_name)

    if not results:
        return {"files": [], "answer": "No relevant code found."}

    # Code context
    context = "\n\n".join(
        [f"{r['path']}:\n{r['text']}" for r in results]
    )

    # Conversation memory
    history_text = "\n".join(
        [f"User: {q}\nAssistant: {r['answer']}" for q, r in chat_history]
    )

    prompt = f"""
You are a senior software engineer analyzing a codebase.

Answer using ONLY the provided code context.

- Mention exact file names
- Explain relationships between components
- Be specific (not generic explanations)
- If unsure, say "not enough context"

Use the conversation history and code context.

Conversation so far:
{history_text}

Context:
{context}

Question:
{query}
Give a precise answer based on both the conversation history and the code context.
"""

    response = llm.invoke(prompt)

    return {
        "files": [r["path"] for r in results],
        "answer": response.content
    }
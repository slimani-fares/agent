import os
import uuid
import chromadb
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# --- Gemini client (embeddings) ---
gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
EMBED_MODEL = "gemini-embedding-001"

def embed(text: str, task_type: str) -> list[float]:
    result = gemini.models.embed_content(
        model=EMBED_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    return result.embeddings[0].values


# --- Chroma client (storage + retrieval) ---
chroma = chromadb.PersistentClient(path="./chroma_store")
collection = chroma.get_or_create_collection(name="memory")


def add(text: str, metadata: dict | None = None) -> None:
    collection.add(
        ids=[uuid.uuid4().hex],
        documents=[text],
        embeddings=[embed(text, "RETRIEVAL_DOCUMENT")],
        metadatas=[metadata or {}],
    )


def search(query: str, k: int = 3) -> list[dict]:
    result = collection.query(
        query_embeddings=[embed(query, "RETRIEVAL_QUERY")],
        n_results=k,
    )
    return [
        {"text": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]
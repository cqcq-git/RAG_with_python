import os
import uuid
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
# use local model
import ollama


# --- 1. SETUP & CONFIGURATION ---
load_dotenv() # load API keys
LLM_MODE = os.getenv("LLM_MODE", "gemini").lower() # Default to gemini if not found

# Load models once at startup to save time on each request
embed_model = SentenceTransformer("BAAI/bge-large-en-v1.5", local_files_only=True)
rerank_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L12-v2', local_files_only=True)

# Google client will now correctly find your GOOGLE_API_KEY from .env
google_client = genai.Client()

# Database Setup
db_path = os.path.join(os.getcwd(), "chroma_storage")
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_or_create_collection(name="RAG_demo_collection")

# --- 2. THE INGESTION ENGINE ---
def initialize_database():
    if collection.count() == 0:
        print("🔍 Database empty. Starting ingestion from doc.md...")
        if os.path.exists("doc.md"):
            with open("doc.md", 'r') as file:
                content = file.read()
            chunks = [chunk for chunk in content.split("\n\n")]
            embeddings = embed_model.encode(chunks, normalize_embeddings=True).tolist()
            ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
            
            collection.add(documents=chunks, embeddings=embeddings, ids=ids)
            print(f"✅ Successfully ingested {len(chunks)} chunks.")
        else:
            print("⚠️ Error: doc.md not found. RAG will have no context!")

# --- 3. DATA MODELS ---
class QueryRequest(BaseModel):
    prompt: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

# --- 4. CORE RAG LOGIC ---
def get_answer(query: str, top_k: int):
    # --- 4a. Retrieval (Search the Vector DB) ---
    query_vec = embed_model.encode(query, normalize_embeddings=True).tolist()
    results = collection.query(query_embeddings=[query_vec], n_results=top_k)
    retrieved_chunks = results['documents'][0]
    
    if not retrieved_chunks:
        return "I don't have any context in my database to answer that.", []

    # --- 4b. Reranking (The "Filter") ---
    pairs = [(query, chunk) for chunk in retrieved_chunks]
    scores = rerank_model.predict(pairs)
    # Sort by score and take the top 3 most relevant ones
    scored_chunks = sorted(zip(retrieved_chunks, scores), key=lambda x: x[1], reverse=True)
    top_chunks = [c for c, s in scored_chunks[:3]]

    # --- 4c. The Prompts ---
    context_text = "\n\n".join([f"[Source {i+1}]: {c}" for i, c in enumerate(top_chunks)])
    system_prompt = "You are a helpful assistant. Answer strictly using the provided context. If the answer is not in the context, say you don't know."
    user_prompt = f"Context:\n{context_text}\n\nQuestion: {query}"

    # --- 4d. THE SWITCH ---
    if LLM_MODE == "ollama":
        print("🤖 Using Local model (Ollama)")
        try:
            response = ollama.chat(
                model='qwen3:4b',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ]
            )
            answer = response['message']['content']
        except Exception as e:
            answer = f"Ollama Error: Ensure 'ollama serve' is running. Detail: {str(e)}", top_chunks
    
    else:
        print("☁️ Using Google Gemini")
        # Combine system and user prompt for Gemini's simple text interface
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = google_client.models.generate_content(
            model="gemini-2.0-flash", # Note: use "2.0-flash" for the latest stable
            contents=full_prompt
        )
        answer = response.text

    return answer, top_chunks

# --- 5. LIFESPAN & APP SETUP ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Project Engine starting...")
    # initialize vector database for RAG
    initialize_database() 
    yield
    print("🛑 Engine shutting down.")
    
app = FastAPI(title="RAG demo API", lifespan=lifespan)
# --- 6. API ENDPOINTS ---

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        # Note: top_k comes from the Pydantic request object now
        answer, sources = get_answer(request.prompt, request.top_k)
        return QueryResponse(answer=answer, sources=sources)
    except Exception as e:
        # This sends a professional error back to the UI/curl
        raise HTTPException(status_code=500, detail=f"RAG Error: {str(e)}")
    


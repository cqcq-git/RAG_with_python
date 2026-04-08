import os
import uuid
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder

# Initialize app and load secrets
load_dotenv() 
app = FastAPI(title=" RAG demo API")

# --- 1. SETUP MODELS  AND DATABASE ---

# Load models once at startup
embed_model = SentenceTransformer("BAAI/bge-large-en-v1.5",local_files_only=True)
rerank_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L12-v2',local_files_only=True)
google_client = genai.Client()

# Use PersistentClient for deployment
db_path = os.path.join(os.getcwd(), "chroma_storage")
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_or_create_collection(name="RAG_demo_collection")

# --- AUTO-INGESTION BLOCK ---
def initialize_database():
    # Check if the collection is already populated
    if collection.count() == 0:
        print("Database empty. Starting ingestion from doc.md...")
        
        # 1. Chunking logic from your notebook
        if os.path.exists("doc.md"):
            with open("doc.md", 'r') as file:
                content = file.read()
            chunks = [chunk for chunk in content.split("\n\n")]
            
            # 2. Embedding logic
            embeddings = embed_model.encode(chunks, normalize_embeddings=True).tolist()
            
            # 3. Save to Persistent DB
            ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
            collection.add(
                documents=chunks,
                embeddings=embeddings,
                ids=ids
            )
            print(f"Successfully ingested {len(chunks)} chunks.")
        else:
            print("Error: doc.md not found in the project directory.")

# Run the ingestion check
initialize_database()


# --- 2. DEFINE DATA MODELS ---
class QueryRequest(BaseModel):
    prompt: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

# --- 3. CORE RAG LOGIC ---
def get_answer(query: str, top_k: int):
    # Embedding
    query_vec = embed_model.encode(query, normalize_embeddings=True).tolist()
    
    # Retrieval
    results = collection.query(query_embeddings=[query_vec], n_results=top_k)
    retrieved_chunks = results['documents'][0]
    
    if not retrieved_chunks:
        return "I don't know.", []

    # Reranking
    pairs = [(query, chunk) for chunk in retrieved_chunks]
    scores = rerank_model.predict(pairs)
    scored_chunks = sorted(zip(retrieved_chunks, scores), key=lambda x: x[1], reverse=True)
    top_chunks = [c for c, s in scored_chunks[:3]]

    # Generation
    context = "\n\n".join([f"[Source {i+1}]: {c}" for i, c in enumerate(top_chunks)])
    prompt = f"Answer strictly using this context:\n{context}\n\nQuestion: {query}"
    
    response = google_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text, top_chunks

# --- 4. API ENDPOINTS ---
@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        answer, sources = get_answer(request.prompt, request.top_k)
        return QueryResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
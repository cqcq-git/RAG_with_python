# RAG Example with Python

This project demonstrates a Retrieval-Augmented Generation (RAG) system implemented in Python. It uses modern NLP techniques to answer questions about documents by retrieving relevant information and generating coherent responses.

## Features

- **FastAPI chatbot API** via `app.py`
- **Chainlit chat UI** via `ui.py`
- **Text embedding** using `sentence-transformers`
- **Reranking** using `cross-encoder/ms-marco-MiniLM-L12-v2`
- **Vector database** using ChromaDB
- **Answer generation** with Google's Gemini 2.5 model via `google-genai`

## Dependencies

The project uses the following key packages:

- `chainlit`: For the interactive chat UI
- `fastapi`: Web API framework
- `uvicorn`: ASGI server
- `sentence-transformers`: For text embedding
- `google-genai`: For Gemini 2.5 integration
- `chromadb`: Vector database for storing and retrieving embeddings
- `python-dotenv`: For environment variable management

## Installation

1. Ensure you have Python 3.12 or higher installed.
2. Install `uv` for dependency management if needed.
3. In the project root, install dependencies:
   ```bash
   uv sync
   ```
4. Create a `.env` file with your Google Gemini API credentials.

## Usage

### Run the FastAPI chatbot API

Start the API server with:
```bash
uv run uvicorn app:app --reload
```

Then send POST requests to:

- `POST /ask`

Request body example:
```json
{
  "prompt": "What is this project about?",
  "top_k": 5
}
```

The API returns an answer and the retrieved source chunks.

### Run the Chainlit chat UI

Start the interactive UI with:
```bash
uv run chainlit run ui.py -w
```

Open the URL shown by Chainlit in your browser to chat with the RAG demo.

## App Behavior

- `app.py` loads embeddings and reranking models at startup.
- It automatically ingests `doc.md` into ChromaDB if the collection is empty.
- `get_answer()` retrieves top chunks, reranks them, and generates a Gemini-based response.
- `ui.py` uses Chainlit to provide a chat interface and display source chunks alongside answers.

## Project Structure

- `app.py`: FastAPI application with RAG inference and `/ask` endpoint
- `ui.py`: Chainlit chat UI that calls `get_answer()` from `app.py`
- `main.ipynb`: Notebook walkthrough of the RAG pipeline
- `doc.md`: Document content used for ingestion
- `pyproject.toml`: Project configuration and dependencies
- `README.md`: This file

## License

Add your license information here.
# RAG Example with Python

This project demonstrates a Retrieval-Augmented Generation (RAG) system implemented in Python. It uses modern NLP techniques to answer questions about documents by retrieving relevant information and generating coherent responses.

## Features

- **Text Embedding**: Utilizes `sentence-transformers` for generating high-quality embeddings from text chunks.
- **Reranking**: Employs cross-encoder models for reranking retrieved documents to improve relevance.
- **Question Answering**: Leverages Google's Gemini 2.5 model (via `google-genai`) to generate answers based on retrieved context.

## Dependencies

The project uses the following key packages:

- `sentence-transformers`: For text embedding
- `google-genai`: For Gemini 2.5 integration
- `chromadb`: Vector database for storing and retrieving embeddings
- `python-dotenv`: For environment variable management

## Installation

1. Ensure you have Python 3.12 or higher installed.
2. Install `uv` for dependency management (if not already installed).
3. Clone or navigate to the project directory.
4. Install dependencies:
   ```bash
   uv sync
   ```

## Usage

The main implementation is in `main.ipynb`, a Jupyter notebook that walks through the RAG pipeline:

1. Document chunking
2. Embedding generation
3. Vector storage with ChromaDB
4. Query processing and retrieval
5. Reranking with cross-encoder
6. Answer generation with Gemini 2.5

To run the notebook:

1. Start Jupyter:
   ```bash
   jupyter notebook
   ```
2. Open `main.ipynb` and execute the cells in order.

Make sure to set up your environment variables (e.g., API keys for Google Gemini) in a `.env` file.

## Project Structure

- `main.py`: Basic entry point (placeholder)
- `main.ipynb`: Main RAG implementation notebook
- `pyproject.toml`: Project configuration and dependencies
- `README.md`: This file

## License

Add your license information here.
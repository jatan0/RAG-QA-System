# RAG Demo

A document Q&A system that lets you ask natural language questions over any PDF and get accurate, grounded answers. Built to understand how vector databases and retrieval-augmented generation work in practice.

## Why I Built This

I built this project to get hands-on experience with vector embeddings and semantic search. These are some concepts I wanted to understand deeply rather than just read about on twitter. Pinecone was the vector database of choice because of its managed infrastructure and clean API, which let me focus on the RAG architecture itself rather than database ops.

The core idea: instead of asking a language model to answer from memory, you retrieve the most relevant chunks of a document first, then pass only that context to the model. This grounds the answer in your actual data and significantly reduces hallucination.

I ran into real tradeoffs during the build. My original chunk size and overlap directly affected retrieval quality, with the model struggling to answer basic questions (i.e. "Where was the telescope launched from and what was it's stated purpose") and I had to tune both based on observed failures. I also learned that vector search has the same basic retrieval tradeoffs as classic keyword search: better recall can introduce noise, while better precision can miss useful context.

## Tech Stack

- **Python 3.x** - Core language
- **Pinecone** - Vector database for storing and querying embeddings
- **OpenAI** - `text-embedding-3-small` for embeddings, `gpt-5.4-nano` for generation
- **LangChain** - PDF loading and text chunking
- **FastAPI** - REST API layer wrapping the query pipeline
- **React + Vite** - Frontend chat interface
- **Uvicorn** - ASGI server

## Features

- Ingest any PDF or folder of PDFs into Pinecone
- Ask natural language questions and get grounded answers
- Retrieves top-k most semantically similar chunks per query
- Displays source page and similarity score for every answer
- Clean chat UI with "Thinking..." state and error handling
- Refuses to answer when retrieved chunks are not relevant

## How It Works

```
PDF → chunk → embed → upsert into Pinecone    (ingest.py, one-time)

Question → embed → query Pinecone → top-k chunks → GPT → answer    (query.py, real-time)
```

Chunk size is set to 1000 characters with 100-character overlap. Overlap prevents context loss at chunk boundaries for questions whose answers span a chunk edge. TOP_K is set to 5, balancing retrieval recall against prompt noise.

## Prerequisites

- Python 3.8+
- Node.js 18+
- Pinecone account (free tier is sufficient)
- OpenAI API key (I only added $5 and the couple of times the program was ran used less than 5 cents of use)

## Installation

1. Clone the repository

```bash
git clone https://github.com/jatan0/rag-demo
cd rag-demo
```

1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

1. Install Python dependencies

```bash
pip install -r requirements.txt
```

1. Set up environment variables — create a `.env` file in the root:

```
PINECONE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

1. Create a Pinecone index with these settings:

- Name: `rag-demo`
- Dimensions: `1536`
- Metric: `cosine`
- Vector type: Dense

2. Install frontend dependencies

```bash
cd frontend
npm install
```

## Usage

**Step 1 — Ingest your PDFs**

Drop any PDF(s) into the `data/` folder, then run: (I like Wikipedia's NASA related articles for testing)

```bash
python ingest.py
```

**Step 2 — Start the backend**

```bash
uvicorn app:app --reload --host 0.0.0.0
```

**Step 3 — Start the frontend**

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` and start asking questions.

## API Endpoints

### Query

**POST** `/query`

```json
{ "question": "Where was the JWST launched from?" }
```

```json
{
	"answer": "From French Guiana, South America, on December 25, 2021.",
	"chunks": [
		{ "text": "...", "source": "data/jwst.pdf", "page": 3, "score": 0.641 }
	]
}
```

### Health Check

**GET** `/health`

```json
{ "status": "ok" }
```

## Project Structure

```
rag-demo/
├── data/               # Drop PDFs here
├── frontend/           # React + Vite UI
│   └── src/
│       ├── App.jsx
│       └── App.css
├── ingest.py           # PDF → chunks → embeddings → Pinecone
├── query.py            # Question → Pinecone → GPT → answer
├── app.py              # FastAPI wrapper around query.py
├── clear_index.py      # Utility to clear all vectors in Pinecone, useful for re-ingesting files
├── requirements.txt
└── .env                # API keys
```

## Key Technical Learnings

- How vector embeddings represent semantic meaning and why cosine similarity works for retrieval
- The precision/recall tradeoff in vector search and how TOP_K and chunk size affect it
- Why RAG produces more grounded answers than prompting a model directly
- How to architect a clean separation between ingestion (offline) and querying (real-time)
- FastAPI's async model and how to run synchronous code without blocking the event loop

## License

MIT

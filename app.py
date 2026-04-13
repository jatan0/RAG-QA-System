import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query import query as rag_query

load_dotenv()

INDEX_NAME = "rag-demo"
TOP_K = 5

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


@app.post("/query")
async def query(request: QueryRequest):
    return await asyncio.to_thread(rag_query, request.question)


@app.get("/health")
async def health():
    return {"status": "ok"}

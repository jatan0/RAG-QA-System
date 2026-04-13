import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

load_dotenv()

DATA_DIR = "data/"
INDEX_NAME = "rag-demo"


def get_pdf_paths(dir_path: str) -> list[str]:
    """Return paths to all .pdf files in dir_path (non-recursive)."""
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"Not a directory: {dir_path}")
    return [
        os.path.join(dir_path, f)
        for f in sorted(os.listdir(dir_path))
        if f.lower().endswith(".pdf")
    ]


def ingest(data_dir: str):
    pdf_paths = get_pdf_paths(data_dir)
    if not pdf_paths:
        print(f"No PDFs found in {data_dir}")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(INDEX_NAME)

    batch_size = 100
    global_chunk_start = 0

    for pdf_path in pdf_paths:
        print(f"Loading {pdf_path}...")
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        print(f"  -> {len(pages)} pages loaded")
        chunks = splitter.split_documents(pages)
        print(f"  -> {len(chunks)} chunks created")

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            vectors = []
            for j, chunk in enumerate(batch):
                embedding = embeddings.embed_query(chunk.page_content)
                idx = global_chunk_start + i + j
                vectors.append(
                    {
                        "id": f"chunk-{idx}",
                        "values": embedding,
                        "metadata": {
                            "text": chunk.page_content,
                            "source": chunk.metadata.get("source", pdf_path),
                            "page": chunk.metadata.get("page", 0),
                        },
                    }
                )
            index.upsert(vectors=vectors)
            start_idx, end_idx = (
                global_chunk_start + i,
                global_chunk_start + i + len(batch) - 1,
            )
            print(f"  -> Upserted chunks {start_idx} to {end_idx}")
        global_chunk_start += len(chunks)

    print("Ingestion complete!")
    print(f"Processed {len(pdf_paths)} PDF(s) from {data_dir}")


if __name__ == "__main__":
    ingest(DATA_DIR)

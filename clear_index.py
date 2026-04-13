import os
from dotenv import load_dotenv

load_dotenv()
# pip install "pinecone[grpc]"
from pinecone import Pinecone

INDEX_NAME = "rag-demo"
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# To get the unique host for an index,
# see https://docs.pinecone.io/guides/manage-data/target-an-index
index = pc.Index(INDEX_NAME)

index.delete(delete_all=True, namespace="__default__")

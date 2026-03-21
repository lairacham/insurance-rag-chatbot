import os
from dotenv import load_dotenv
from pymilvus import MilvusClient
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

# Get the variables from the .env file
ZILLIZ_ENDPOINT = os.getenv('ZILLIZ_ENDPOINT')
ZILLIZ_TOKEN = os.getenv('ZILLIZ_TOKEN')
ZILLIZ_USER = os.getenv('ZILLIZ_USER')
ZILLIZ_PASSWORD = os.getenv('ZILLIZ_PASSWORD')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

client = MilvusClient(
    uri=ZILLIZ_ENDPOINT,
    token=ZILLIZ_TOKEN,
)

# TODO: Update to paid model after testing
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def retrieve(query: str, top_k: int = 3) -> str:
    vector = embeddings.embed_query(query)
    results = client.search(
        collection_name="insurance_kb",
        data=[vector],
        limit=top_k,
        output_fields=["text"],
    )
    chunks = [hit["entity"]["text"] for hit in results[0]]
    return "\n\n".join(chunks)

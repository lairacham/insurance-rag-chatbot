import os
from dotenv import load_dotenv
from pymilvus import MilvusClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from openai import OpenAI

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

openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

def embed(text: str) -> list[float]:
    embeddings = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return embeddings.data[0].embedding

def retrieve(query: str, top_k: int = 3) -> str:
    vector = embed(query)
    results = client.search(
        collection_name="insurance_kb",
        data=[vector],
        limit=top_k,
        output_fields=["text"],
    )
    chunks = [hit["entity"]["text"] for hit in results[0]]
    return "\n\n".join(chunks)

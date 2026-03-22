import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pymilvus import MilvusClient

load_dotenv()

# Get the variables from the .env file
ZILLIZ_ENDPOINT = os.getenv('ZILLIZ_ENDPOINT')
ZILLIZ_TOKEN = os.getenv('ZILLIZ_TOKEN')
ZILLIZ_USER = os.getenv('ZILLIZ_USER')
ZILLIZ_PASSWORD = os.getenv('ZILLIZ_PASSWORD')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

client = MilvusClient(
    uri=ZILLIZ_ENDPOINT,
    token=ZILLIZ_TOKEN,
)

def load_documents():
    """
    Load documents from the knowledge-base directory
    """
    loader = DirectoryLoader("knowledge-base/", glob="**/*.md", loader_cls=TextLoader)
    pages = loader.load()
    print(f"Loaded {len(pages)} documents.")
    return pages

def split_documents(documents):
    """
    Split documents into chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50, 
        length_function=len, 
        add_start_index=True,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} into {len(chunks)} chunks.")
    return chunks

def upload_embeddings(embeddings, chunks):
    """
    Upload embeddings to Zilliz
    """
    texts = [chunk.page_content for chunk in chunks]
    vectors = embeddings

    data = [
        {
            "vector": vectors[i], 
            "text": texts[i]
        } 
        for i in range(len(chunks))
    ]

    result = client.insert(collection_name="insurance_kb", data=data)

    print(f"Inserted {result['insert_count']} chunks!")

def embed(text: str) -> list[float]:
    embeddings = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return embeddings.data[0].embedding

def main():
    documents = load_documents()

    chunks = split_documents(documents)

    embeddings = [embed(chunk.page_content) for chunk in chunks]
    
    # Embed the chunks and upload to Zilliz
    upload_embeddings(embeddings=embeddings, chunks=chunks)

    return None


if __name__ == "__main__":
    main()

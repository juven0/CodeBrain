import os

from pinecone import Pinecone, ServerlessSpec
from vectorizer import GeminiEmbedder
from chunk import Chunk
from uuid import uuid4

store = Pinecone(api_key= os.getenv("PINECONE_API_KEY"))

index_name = os.getenv("PINECONE_INDEX_NAME")

if index_name not in store.list_indexes().names():
    store.create_index(
        name= index_name,
        dimension= 768, #specific for GEMINI model
        metric= "cosine",
        spec= ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )

    )

index = store.Index(index_name)
embeder = GeminiEmbedder()

def upsertChunks(index, chunks:Chunk):
    vectors = []

    for chunk in chunks:
        embeding = embeder.embed_document(chunk.to_embedding())

        vectors.append({
            "id": uuid4(),
            "values":embeding,
            "metadata": {
                "filePath": chunk.Path,
                "name": chunk.name,
                "type": chunk.type,
                "language": chunk.language,
                "code": chunk.code,
                #"calls": chunk.calls
                "imports": chunk.imports
            }
        })
    
    index.upsert(vectors=vectors)

def queryIndex(index, query: str):
    query_embedding = embeder.embed_query(query)

    result = index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True
    )

    return result
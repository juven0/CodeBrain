import os
from uuid import uuid4
from typing import List
from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec
from vectorizer import GeminiEmbedder
from chunk import Chunk


class PineconeVectorStore:

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")

        self.store = Pinecone(api_key=self.api_key)

        self._ensure_index()

        self.index = self.store.Index(self.index_name)

        self.embedder = GeminiEmbedder()

    def _ensure_index(self):
        print(self.index_name)
        if self.index_name not in self.store.list_indexes().names():
            self.store.create_index(
                name=self.index_name,
                dimension=768,  # Gemini embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

    def upsert_chunks(self, chunks: List[Chunk]):

        vectors = []
        for chunk in chunks:
            embedding = self.embedder.embed_document(
                chunk.to_embedding()
            ).embeddings[0].values
            print(embedding)
            vectors.append({
                "id": str(uuid4()),
                "values": embedding,
                "metadata": {
                    "filePath": chunk.path,
                    "name": chunk.name,
                    "type": chunk.type,
                    "language": chunk.language,
                    "code": chunk.code,
                    "imports":  ", ".join(chunk.imports)
                }
            })
        if len(vectors)>0:
            self.index.upsert(vectors=vectors)

    def query(self, query: str, top_k: int = 5):

        query_embedding = self.embedder.embed_query(query).embeddings[0].values

        result = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        return result
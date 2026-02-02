import chromadb
from langchain import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings 

def query_chroma_db(query: str):
    client = chromadb.Client()
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    vector_store = Chroma(client=client, embedding_function=embeddings)
    
    results = vector_store.similarity_search(query)
    
    return results